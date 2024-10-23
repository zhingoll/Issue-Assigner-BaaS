from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import torch
import pandas as pd
import torch.nn as nn

def construct_index(G, issue_contents_df):
    # 获取所有的Issue和User节点
    issue_nodes = [n for n, attr in G.nodes(data=True) if attr['node_type'] == 'Issue']
    user_nodes = [n for n, attr in G.nodes(data=True) if attr['node_type'] == 'User']

    # 创建节点到索引的映射
    node_encoder = LabelEncoder()
    all_nodes = issue_nodes + user_nodes
    node_encoder.fit(all_nodes)

    # 节点名称到索引的映射
    node_to_index = {node: idx for idx, node in enumerate(node_encoder.classes_)}

    # 构建边索引
    edge_index = []
    edge_weight = []

    for u, v, data in G.edges(data=True):
        u_idx = node_to_index[u]
        v_idx = node_to_index[v]
        weight = data['weight']
        edge_index.append([u_idx, v_idx])
        edge_index.append([v_idx, u_idx])  # 无向图，需要双向边
        edge_weight.append(weight)
        edge_weight.append(weight)
    edge_index = torch.tensor(edge_index, dtype=torch.long).t()
    edge_weight = torch.tensor(edge_weight, dtype=torch.float)

    # 合并Issue内容数据和图中的Issue节点
    issue_df = pd.DataFrame({'issue_number': issue_nodes})
    print(issue_df['issue_number'].dtype)
    print(issue_contents_df['number'].dtype)
    # issue_df['issue_number'] = issue_df['issue_number'].astype(int)
    issue_contents_df['number'] = issue_contents_df['number'].astype(str)
    issue_df = issue_df.merge(issue_contents_df, left_on='issue_number', right_on='number', how='left')

    # 处理缺失值
    issue_df['title'] = issue_df['title'].fillna('')
    issue_df['body'] = issue_df['body'].fillna('')

    # 文本预处理和特征提取
    issue_df['text'] = issue_df['title'] + ' ' + issue_df['body']

    # 使用TF-IDF向量化
    vectorizer = TfidfVectorizer(max_features=128)
    issue_features = vectorizer.fit_transform(issue_df['text']).toarray()

    #     # 简单起见，将User节点的特征初始化为零向量
    #     user_features = np.zeros((len(user_nodes), issue_features.shape[1]))
    #     # 合并所有节点特征
    #     node_features = np.vstack([issue_features, user_features])
    #     x = torch.tensor(node_features, dtype=torch.float)

    # 定义用户嵌入
    num_users = len(user_nodes)
    embedding_dim = issue_features.shape[1]
    user_embeddings = nn.Embedding(num_users, embedding_dim)

    # 初始化用户嵌入
    nn.init.xavier_uniform_(user_embeddings.weight)

    # 合并所有节点特征
    issue_features = torch.tensor(issue_features, dtype=torch.float)
    x = torch.cat([issue_features, user_embeddings.weight], dim=0)

    return node_to_index, edge_index, edge_weight, x, issue_nodes, user_nodes, user_embeddings, vectorizer, node_encoder
