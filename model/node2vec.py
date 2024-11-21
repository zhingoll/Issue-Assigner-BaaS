from .registry import ModelRegistry
from .graphbasemodel import GraphBaseModel
import os
import torch
from torch_geometric.nn import Node2Vec
import torch.nn.functional as F
import torch.nn as nn
from torch_geometric.loader import LinkNeighborLoader, NeighborLoader
from datetime import datetime, timezone
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from torch_geometric.utils import negative_sampling

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@ModelRegistry.register('node2vec')
class Node2VecModel(GraphBaseModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.embedding_dim = int(self.config["hyperparameter"].get('embedding_dim', 64))
        self.walk_length = int(self.config["hyperparameter"].get('walk_length', 20))
        self.context_size = int(self.config["hyperparameter"].get('context_size', 10))
        self.walks_per_node = int(self.config["hyperparameter"].get('walks_per_node', 10))
        self.num_negative_samples = int(self.config["hyperparameter"].get('num_negative_samples', 1))
        # self.sparse = self.config["hyperparameter"].get('sparse', True)
        self.batch_size = int(self.config["batch_size"])
        self.learning_rate = float(self.config["learningRate"])
        self.epoch = int(self.config["epoch"])
        self.topk = int(self.config["topk"])
        self.criterion = nn.BCEWithLogitsLoss()
        

    def train(self):
        self.node2vec = Node2Vec(
            edge_index=self.data.edge_index,
            embedding_dim=self.embedding_dim,
            walk_length=self.walk_length,
            context_size=self.context_size,
            walks_per_node=self.walks_per_node,
            num_negative_samples=self.num_negative_samples,
            # sparse=self.sparse
        ).to(device)
        self.optimizer = torch.optim.Adam(list(self.node2vec.parameters()), lr=self.learning_rate)
        self.log.info('Training Node2Vec Embeddings...')
        self.node2vec.train()
        loader = self.node2vec.loader(batch_size=self.batch_size, shuffle=True)
        for epoch in range(1, self.epoch + 1):
            total_loss = 0
            for pos_rw, neg_rw in loader:
                self.optimizer.zero_grad()
                loss = self.node2vec.loss(pos_rw.to(device), neg_rw.to(device))
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            avg_loss = total_loss / len(loader)
            self.log.info(f'Epoch: {epoch:03d}, Loss: {avg_loss:.4f}')
        self.log.info('Node2Vec Embeddings Training Complete.')
        self.node_embeddings = self.node2vec.embedding.weight.detach()

    def validate(self):
        self.log.info('Validating...')
        self.node2vec.eval()
        total_loss = 0
        preds = []
        labels = []
        with torch.no_grad():
            # 使用验证集的正负样本进行评估
            edge_label_index = self.val_data.edge_label_index
            edge_label = self.val_data.edge_label

            src = edge_label_index[0]
            dst = edge_label_index[1]

            src_emb = self.node_embeddings[src]
            dst_emb = self.node_embeddings[dst]

            pred = (src_emb * dst_emb).sum(dim=-1)
            loss = self.criterion(pred, edge_label.float().to(device))
            total_loss = loss.item()

            preds = pred.cpu()
            labels = edge_label.cpu()
            pred_labels = (torch.sigmoid(preds) > 0.4).float()
            accuracy = accuracy_score(labels, pred_labels)
            f1 = f1_score(labels, pred_labels)
            auc = roc_auc_score(labels.numpy(), torch.sigmoid(preds).numpy())
            self.log.info(f'Validation Loss: {total_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}')

    def test(self):
        self.log.info('Testing...')
        self.node2vec.eval()
        with torch.no_grad():
            # 获取用户嵌入（假设 node_type == 0 表示用户）
            user_indices = torch.arange(self.data.num_nodes)[self.data.node_type == 0].to(device)
            user_embs = self.node_embeddings[user_indices]
            # 创建反向 user 映射
            user_mapping_inv = {idx: user for user, idx in self.user_mapping.items()}
            # 创建反向 issue 映射
            issue_mapping_inv = {idx: number for number, idx in self.issue_mapping.items()}

            # 处理测试集中的 issue
            for batch in self.test_loader:
                batch = batch.to(device)
                issue_indices = batch.n_id
                issue_embs = self.node_embeddings[issue_indices]

                # 计算 issue 与所有用户之间的相似度
                scores = torch.matmul(issue_embs, user_embs.T)  # [num_issues, num_users]
                probabilities = torch.sigmoid(scores)

                # 获取每个 issue 的前 K 个用户
                top_k = self.topk
                top_k_scores, top_k_indices = torch.topk(probabilities, k=top_k, dim=1)

                # 将用户索引映射为用户名
                user_indices_np = user_indices[top_k_indices].cpu().numpy()
                user_names_array = np.vectorize(user_mapping_inv.get)(user_indices_np)

                # 获取对应的 issue 编号
                issue_global_indices = issue_indices.cpu().numpy()
                issue_numbers = [issue_mapping_inv[idx] for idx in issue_global_indices]

                # 保存预测结果
                for issue_number, user_names, scores in zip(issue_numbers, user_names_array, top_k_scores.cpu().numpy()):
                    probabilities_list = scores.tolist()
                    user_names_list = user_names.tolist()
                    self.save_issue_assign(
                        self.owner, self.name, issue_number,
                        probabilities_list, user_names_list, self.issue_assign_collection
                    )

    # def save_issue_assign(self, owner, name, number, probability, assignees, issue_assign_collection):
    #     data = {
    #         "owner": owner,
    #         "name": name,
    #         "number": number,
    #         "model":self.model_name,
    #         "probability": probability,
    #         "last_updated": datetime.now(timezone.utc),
    #         "assignee": assignees
    #     }
    #     # 更新或插入数据
    #     issue_assign_collection.update_one(
    #         {"owner": owner, "name": name, "number": number,"model":self.model_name},
    #         {"$set": data},
    #         upsert=True
    #     )
