from .registry import ModelRegistry
from .graphbasemodel import GraphBaseModel
import os
from torch_geometric.nn import SAGEConv,HeteroConv
import torch.nn.functional as F
import torch.nn as nn
from torch_geometric.nn.conv import GraphConv
import torch
from datetime import datetime, timezone
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

@ModelRegistry.register('hgraphsage')
class HGraphSage(GraphBaseModel):
    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.in_channels = int(self.config["hyperparameter"]['in_channels'])
        self.hidden_channels = int(self.config["hyperparameter"]['hidden_channels'])
        self.out_channels = int(self.config["hyperparameter"]['out_channels'])
        self.dropout = int(self.config["hyperparameter"]['dropout'])
        self.model = HeteroGraphSAGE(self.in_channels,self.hidden_channels, self.out_channels,self.dropout).to(device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learningRate)
        self.criterion = nn.BCEWithLogitsLoss()
    
    def train(self):
        self.model.train()
        for epoch in range(self.epoch):
            preds = []
            labels = []
            total_loss = 0
            for batch in self.train_loader:
                self.optimizer.zero_grad()
                batch = batch.to(device)
                x_dict = batch.x_dict
                edge_index_dict = batch.edge_index_dict
                
                # 构建 edge_weight_dict
                edge_weight_dict = {}
                for rel in edge_index_dict.keys():
                    if 'edge_weight' in batch[rel]:
                        edge_weight_dict[rel] = batch[rel].edge_weight
                    else:
                        edge_weight_dict[rel] = None
                
                out_dict = self.model(x_dict, edge_index_dict,edge_weight_dict)
                
                issue_emb = out_dict['issue']
                user_emb = out_dict['user']
                src = batch['issue', 'resolved_by', 'user'].edge_label_index[0]
                dst = batch['issue', 'resolved_by', 'user'].edge_label_index[1]
                
                src_emb = issue_emb[src]
                dst_emb = user_emb[dst]
                
                pred = (src_emb * dst_emb).sum(dim=-1)
                loss = self.criterion(pred, batch['issue', 'resolved_by', 'user'].edge_label.float())
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
                preds.append(pred.cpu())
                labels.append(batch['issue', 'resolved_by', 'user'].edge_label.cpu()) 

            self.log.info(f'Epoch {epoch+1}/{self.epoch}, Loss: {total_loss:.4f}')       
            preds = torch.cat(preds)
            labels = torch.cat(labels)
            pred_labels = (preds > 0.4).float()
            accuracy = accuracy_score(labels, pred_labels)
            f1 = f1_score(labels, pred_labels)
            auc = roc_auc_score(labels.detach().numpy(), preds.detach().numpy())
            self.log.info(f'Train Loss: {total_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}')

    def validate(self):
        self.model.eval()
        total_loss = 0
        preds = []
        labels = []
        with torch.no_grad():
            for batch in self.val_loader:
                batch = batch.to(device)
                x_dict = batch.x_dict
                edge_index_dict = batch.edge_index_dict
                
                edge_weight_dict = {}
                for rel in edge_index_dict.keys():
                    if 'edge_weight' in batch[rel]:
                        edge_weight_dict[rel] = batch[rel].edge_weight
                    else:
                        edge_weight_dict[rel] = None
                
                out_dict = self.model(x_dict, edge_index_dict,edge_weight_dict)
                
                issue_emb = out_dict['issue']
                user_emb = out_dict['user']
                
                src = batch['issue', 'resolved_by', 'user'].edge_label_index[0]
                dst = batch['issue', 'resolved_by', 'user'].edge_label_index[1]
                
                src_emb = issue_emb[src]
                dst_emb = user_emb[dst]
                
                pred = (src_emb * dst_emb).sum(dim=-1)
                loss = self.criterion(pred, batch['issue', 'resolved_by', 'user'].edge_label.float())
                total_loss += loss.item()               
                preds.append(pred.cpu())
                labels.append(batch['issue', 'resolved_by', 'user'].edge_label.cpu())

        preds = torch.cat(preds)
        labels = torch.cat(labels)
        pred_labels = (preds > 0.4).float()
        accuracy = accuracy_score(labels, pred_labels)
        f1 = f1_score(labels, pred_labels)
        auc = roc_auc_score(labels.detach().numpy(), preds.detach().numpy())
        self.log.info(f'Validate Loss: {total_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}, AUC: {auc:.4f}')

    def save_issue_assign(self,owner, name, number, probability, assignees,issue_assign_collection):
        data = {
            "owner": owner,
            "name": name,
            "number": number,
            "probability": probability,
            "last_updated": datetime.now(timezone.utc),
            "assignee": assignees
        }
        # 更新或插入数据
        issue_assign_collection.update_one(
            {"owner": owner, "name": name, "number": number},
            {"$set": data},
            upsert=True
        )

    # # 对于大规模图，分批次进行user embedding的保存
    # def get_allnode_emb(self):
    #     self.user_loader = NeighborLoader(
    #                 self.data,
    #                 num_neighbors=[-1],  # 可以根据需要设置采样的邻居数
    #                 input_nodes=('user', torch.arange(self.data['user'].num_nodes)),
    #                 batch_size=self.batch_size,
    #                 shuffle=False
    #             )
    #     self.model.eval()
    #     user_emb_list = []
    #     with torch.no_grad():
    #         for batch in self.user_loader:
    #             batch = batch.to(device)
    #             x_dict = batch.x_dict
    #             edge_index_dict = batch.edge_index_dict

    #             edge_weight_dict = {}
    #             for rel in edge_index_dict.keys():
    #                 if 'edge_weight' in batch[rel]:
    #                     edge_weight_dict[rel] = batch[rel].edge_weight
    #                 else:
    #                     edge_weight_dict[rel] = None

    #             # 前向传播，计算用户嵌入
    #             out_dict = self.model(x_dict, edge_index_dict, edge_weight_dict)
    #             user_emb = out_dict['user']

    #             # 获取批次内的全局用户节点索引
    #             global_user_indices = batch['user'].n_id.cpu()

    #             # 将嵌入和索引保存下来
    #             user_emb_list.append((global_user_indices, user_emb.cpu()))
        
    #     # 根据全局用户索引，将嵌入拼接成完整的用户嵌入张量
    #     num_users = self.data['user'].num_nodes
    #     self.user_emb = torch.zeros((num_users, self.out_channels))
    #     for indices, emb in user_emb_list:
    #         self.user_emb[indices] = emb
    #     print("所有用户的嵌入已计算并保存，形状为：", self.user_emb.shape)

    # 对于中小规模图，一次整张图的前向传播得到user的embedding并保存    
    def get_allnode_emb(self):
        self.model.eval()
        with torch.no_grad():
            self.data = self.data.to(device)
            x_dict = self.data.x_dict
            edge_index_dict = self.data.edge_index_dict
            edge_weight_dict = {}
            for rel in edge_index_dict.keys():
                if 'edge_weight' in self.data[rel]:
                    edge_weight_dict[rel] = self.data[rel].edge_weight
                else:
                    edge_weight_dict[rel] = None
            out_dict = self.model(x_dict, edge_index_dict, edge_weight_dict)
            self.user_emb = out_dict['user']
        print("所有用户的嵌入已计算并保存，形状为：", self.user_emb.shape)

    # 对未来做预测，都是全新的issue，没有ground-truth,没有任何交互信息
    def test(self):
        self.get_allnode_emb()
        self.model.eval()
        with torch.no_grad():
            for subgraph in self.test_loader:
                subgraph = subgraph.to(device)
                x_dict = subgraph.x_dict
                edge_index_dict = subgraph.edge_index_dict

                edge_weight_dict = {}
                for rel in edge_index_dict.keys():
                    if 'edge_weight' in subgraph[rel]:
                        edge_weight_dict[rel] = subgraph[rel].edge_weight
                    else:
                        edge_weight_dict[rel] = None

                # 前向传播
                out_dict = self.model(x_dict,edge_index_dict,edge_weight_dict)
                # issue_emb = self.model.issue_mlp(x_dict['issue'])
                issue_emb = out_dict['issue']  # [batch_size, out_channels]

                # 获取 batch 中的 issue 索引
                # issue_batch = subgraph['issue'].batch  # [batch_size]
                # 对于每个 issue，计算与所有用户的相似度
                scores = torch.matmul(self.user_emb, issue_emb.T).T  # [batch_size, num_users]
                probabilities = torch.sigmoid(scores)

                # 获取每个 issue 的前 K 个用户
                top_k = 10
                top_k_scores, top_k_indices = torch.topk(probabilities, k=top_k, dim=1)  # [batch_size, top_k]

                # 将用户索引映射为用户名
                user_indices_np = top_k_indices.cpu().numpy()
                # 创建反向user映射
                user_mapping_inv = {idx: user for user, idx in self.user_mapping.items()}
                # 遍历user_indices_np中的每个元素（每个用户索引）,使用user_mapping_inv.get 查询每个索引对应的用户名
                user_names_array = np.vectorize(user_mapping_inv.get)(user_indices_np)

                # 获取对应的 issue 编号
                issue_global_indices = subgraph['issue'].n_id.cpu().numpy()  # 全局索引
                # 创建反向issue映射
                issue_mapping_inv = {idx: number for number, idx in self.issue_mapping.items()}
                open_issue_numbers = [issue_mapping_inv[idx] for idx in issue_global_indices]

                # 保存预测结果
                for issue_number, user_names, scores in zip(open_issue_numbers, user_names_array, top_k_scores.cpu().numpy()):
                    probabilities_list = scores.tolist()
                    user_names_list = user_names.tolist()
                    self.save_issue_assign(
                        self.owner, self.name, issue_number,
                        probabilities_list, user_names_list, self.issue_assign_collection
                    )


class HeteroGraphSAGE(nn.Module):
    def __init__(self,in_channels,hidden_channels, out_channels, dropout):
        super(HeteroGraphSAGE, self).__init__()
        self.issue_mlp = nn.Linear(in_channels, in_channels)

        self.conv1 = HeteroConv({
            ('user', 'participate', 'issue'): GraphConv((-1, -1), hidden_channels),
            ('issue', 'rev_participate', 'user'): GraphConv((-1, -1), hidden_channels),
            # 可以添加其他关系
        }, aggr='mean')
        
        self.conv2 = HeteroConv({
            ('user', 'participate', 'issue'): GraphConv(hidden_channels, out_channels),
            ('issue', 'rev_participate', 'user'): GraphConv(hidden_channels, out_channels),
            # 可以添加其他关系
        }, aggr='mean')
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=dropout)
    
    def forward(self, x_dict, edge_index_dict, edge_weight_dict=None):
        x_dict = x_dict.copy() 
        # 对节点特征进行初步处理
        x_dict['issue'] = self.issue_mlp(x_dict['issue'])
        # 然后进行消息传递           
        x_dict = self.conv1(x_dict, edge_index_dict, edge_weight_dict=edge_weight_dict)
        x_dict = {key: self.relu(x) for key, x in x_dict.items()}
        x_dict = {key: self.dropout(x) for key, x in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict, edge_weight_dict=edge_weight_dict)
        return x_dict

  