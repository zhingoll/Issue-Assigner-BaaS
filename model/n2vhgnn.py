from .registry import ModelRegistry
from .graphbasemodel import GraphBaseModel
import os
import torch
from torch_geometric.nn import Node2Vec
import torch.nn.functional as F
import torch.nn as nn
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import easygraph as eg

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@ModelRegistry.register('n2vhgnn')
class N2VHGNN(GraphBaseModel):
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
        self.in_channels = int(self.config["hyperparameter"].get('in_channels', 64))
        self.hidden_channels = int(self.config["hyperparameter"].get('hidden_channels', 128))
        self.out_channels = int(self.config["hyperparameter"].get('out_channels', 64))
        self.model = eg.HGNN(in_channels = self.in_channels , hid_channels = self.hidden_channels,
                     num_classes = self.out_channels).to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.BCEWithLogitsLoss()
        

    def pre_train(self):
        self.node2vec = Node2Vec(
            edge_index=self.data.edge_index,
            embedding_dim=self.embedding_dim,
            walk_length=self.walk_length,
            context_size=self.context_size,
            walks_per_node=self.walks_per_node,
            num_negative_samples=self.num_negative_samples,
            # sparse=self.sparse
        ).to(device)
        self.n2v_optimizer = torch.optim.Adam(self.node2vec.parameters(), lr=self.learning_rate)
        self.log.info('Pre-Training Node2Vec Embeddings...')
        self.node2vec.train()
        loader = self.node2vec.loader(batch_size=self.batch_size, shuffle=True)
        for epoch in range(1, self.epoch + 1):
            total_loss = 0
            for pos_rw, neg_rw in loader:
                self.n2v_optimizer.zero_grad()
                loss = self.node2vec.loss(pos_rw.to(device), neg_rw.to(device))
                loss.backward()
                self.n2v_optimizer.step()
                total_loss += loss.item()
            # avg_loss = total_loss / len(loader)
            # self.log.info(f'Epoch: {epoch:03d}, Loss: {avg_loss:.4f}')
        self.log.info('Node2Vec Embeddings Pre-Training Complete.')
        self.node_embeddings = self.node2vec.embedding.weight.detach()

    def train(self):
        self.pre_train()
        self.model.train()
        for epoch in range(self.epoch):
            total_loss = 0
            preds = []
            labels = []
            for batch in self.train_loader:
                batch = batch.to(device)
                batch_node_indices = batch.n_id  # 全局索引
                batch_node_embeddings = self.node_embeddings[batch_node_indices].to(device)
                batch_hg = eg.Hypergraph.from_feature_kNN(batch_node_embeddings, k=3).to(device)
                outputs = self.model(batch_node_embeddings, batch_hg)
                src = batch.edge_label_index[0]
                dst = batch.edge_label_index[1]
                src_emb = outputs[src]
                dst_emb = outputs[dst]
                pred = (src_emb * dst_emb).sum(dim=-1)
                loss = self.criterion(pred, batch.edge_label.float())
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
                preds.append(pred.cpu())
                labels.append(batch.edge_label.cpu())

            self.log.info(f'Epoch {epoch+1}/{self.epoch}, Loss: {total_loss:.4f}')       
            preds = torch.sigmoid(torch.cat(preds))
            labels = torch.cat(labels)
            pred_labels = (preds > 0.6).float()
            accuracy = accuracy_score(labels, pred_labels)
            f1 = f1_score(labels, pred_labels)
            auc = roc_auc_score(labels.detach().numpy(), preds.detach().numpy())
            self.log.info(f'Train Loss: {total_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}')

    def validate(self):
        self.log.info('Validating...')
        self.model.eval()
        total_loss = 0
        preds = []
        labels = []
        with torch.no_grad():
            for batch in self.val_loader:
                batch = batch.to(device)
                batch_node_indices = batch.n_id
                batch_node_embeddings = self.node_embeddings[batch_node_indices].to(device)
                batch_hg = eg.Hypergraph.from_feature_kNN(batch_node_embeddings, k=3).to(device)
                outputs = self.model(batch_node_embeddings, batch_hg)

                src = batch.edge_label_index[0]
                dst = batch.edge_label_index[1]
                src_emb = outputs[src]
                dst_emb = outputs[dst]
                pred = (src_emb * dst_emb).sum(dim=-1)

                loss = self.criterion(pred, batch.edge_label.float())
                total_loss += loss.item()

                preds.append(pred.cpu())
                labels.append(batch.edge_label.cpu())

        preds = torch.sigmoid(torch.cat(preds))
        labels = torch.cat(labels)
        pred_labels = (preds > 0.6).float()
        accuracy = accuracy_score(labels, pred_labels)
        f1 = f1_score(labels, pred_labels)
        auc = roc_auc_score(labels.detach().numpy(), preds.detach().numpy())
        self.log.info(f'Validate Loss: {total_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}')

    def test(self):
        self.log.info('Testing...')
        self.model.eval()
        with torch.no_grad():
            # 获取所有节点的嵌入
            node_embeddings = self.node_embeddings.to(device)

            # 构建包含所有节点的超图
            hg = eg.Hypergraph.from_feature_kNN(node_embeddings, k=3).to(device)
            # 获取所有节点的更新嵌入
            outputs = self.model(node_embeddings, hg)

            # 获取用户节点和 issue 节点的索引
            user_indices = torch.arange(self.data.num_nodes)[self.data.node_type == 0].to(device)
            # issue_indices_all = torch.arange(self.data.num_nodes)[self.data.node_type == 1].to(device)

            # 从更新的节点嵌入中提取用户和 issue 节点的嵌入
            user_embs = outputs[user_indices]
            # issue_embs_all = outputs[issue_indices_all]

            # 创建反向映射
            user_mapping_inv = {idx: user for user, idx in self.user_mapping.items()}
            issue_mapping_inv = {idx: number for number, idx in self.issue_mapping.items()}

            # 处理测试集中的 issue 节点
            for batch in self.test_loader:
                batch = batch.to(device)
                issue_indices = batch.n_id  # 测试批次中的 issue 节点索引

                # 从更新的节点嵌入中提取对应的 issue 节点嵌入
                issue_embs = outputs[issue_indices]

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

    
