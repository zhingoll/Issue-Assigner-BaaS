import os
import torch
import pandas as pd
from torch_geometric.data import InMemoryDataset, HeteroData
from sklearn.feature_extraction.text import TfidfVectorizer
from torch_geometric.transforms import ToUndirected
from tools.nlp import clean_text
import torch.nn as nn

class IssueAssignDataset(InMemoryDataset):
    def __init__(self, root,transform=None, pre_transform=None):
        super(IssueAssignDataset, self).__init__(root,transform, pre_transform)
        self.load(self.processed_paths[0])
        

    @property
    def raw_file_names(self):
        # 返回需要处理的原始文件列表
        return ['issue_content.csv', 'user_issue.csv','resolved_issues.csv','opened_issues.csv']

    @property
    def processed_file_names(self):
        # 返回处理后的数据文件名
        return ['data.pt']

    def download(self):
        pass

    def process(self):
        # 定义文件路径
        issue_content_path = os.path.join(self.raw_dir, 'issue_content.csv')
        user_issue_path = os.path.join(self.raw_dir, 'user_issue.csv')
        resolved_issues_path = os.path.join(self.raw_dir, 'resolved_issues.csv')
        # 测试集所使用的数据
        opened_issues_path = os.path.join(self.raw_dir, 'opened_issues.csv')
        dim = 64

        # 准备文本特征提取器
        title_vectorizer = TfidfVectorizer(max_features=(dim//2))
        body_vectorizer = TfidfVectorizer(max_features=(dim//2))

        # 加载 issue 节点数据
        issue_x, issue_mapping = self.get_node_mapping(
            issue_content_path, 'number',
            encoders={
                'title': lambda x: title_vectorizer.fit_transform(x).toarray(),
                'body': lambda x: body_vectorizer.fit_transform(x).toarray()
            },
            cleaners={
                'title': clean_text,
                'body': clean_text
            }
        )

    # 加载未解决的 Issue 数据
        opened_issues_df = pd.read_csv(opened_issues_path)

        open_issue_x, open_issue_mapping = self.get_node_mapping(
            opened_issues_path, 'number',
            encoders={
                'title': lambda x: title_vectorizer.transform(x).toarray(),
                'body': lambda x: body_vectorizer.transform(x).toarray()
            },
            cleaners={
                'title': clean_text,
                'body': clean_text
            }
        )

        # 合并 issue_mapping和issue_x
        for number, idx in open_issue_mapping.items():
            if number not in issue_mapping:
                issue_mapping[number] = len(issue_mapping)
                issue_x = torch.cat([issue_x, open_issue_x[idx].unsqueeze(0)], dim=0)
            else:
                # 如果 issue 已存在，跳过或更新特征
                pass


        # 加载 user 节点数据,目前没结合用户信息
        _, user_mapping = self.get_node_mapping(user_issue_path, 'UserName')
        
        
        # 更新 user_mapping
        for opener in opened_issues_df['user']:
            if opener not in user_mapping:
                user_mapping[opener] = len(user_mapping)

        # 更新user_embedding
        user_embedding = nn.Embedding(len(user_mapping),dim)

        # 标记 open_issues
        is_open_issue = torch.zeros(len(issue_mapping), dtype=torch.bool)
        for number in opened_issues_df['number']:
            idx = issue_mapping[number]
            is_open_issue[idx] = True
        

        # 添加 'user', 'open', 'issue' 边
        opener_indices = []
        issue_indices = []
        for _, row in opened_issues_df.iterrows():
            opener = row['user']
            issue_number = row['number']
            opener_idx = user_mapping[opener]
            issue_idx = issue_mapping[issue_number]
            opener_indices.append(opener_idx)
            issue_indices.append(issue_idx)
        open_edge_index = torch.tensor([opener_indices, issue_indices], dtype=torch.long)
        

        # # 定义边的权重,参考OpenRank(https://dl.acm.org/doi/10.1145/3639477.3639734)
        # weight_mapping = {
        #     'PR_OPEN': 0.45,
        #     'COMMENTED': 0.06,
        #     'REVIEW_COMMENT': 0.10,
        #     'ISSUE_OPEN': 0.25,
        #     'LABELED': 0.04,
        #     'NORMAL_COMMENT': 0.10
        # }
        # 目前不关注边的行为，仅让模型从参与行为中识别谁是解决者
        weight_mapping = {
            'PR_OPEN': 1,
            'COMMENTED': 1,
            'REVIEW_COMMENT': 1,
            'ISSUE_OPEN': 1,
            'LABELED': 1,
            'NORMAL_COMMENT': 1
        }

        # 加载边数据
        edge_index, _, edge_weight = self.get_edge_index(
            user_issue_path,
            'UserName', user_mapping,
            'IssueNumber', issue_mapping,
            weight_mapping=weight_mapping,
            weight_col='EventType'
        )

        # 加载 开发者-解决-issue 数据(训练标签)
        pos_edge_index = self.get_resolved_edges(
            resolved_issues_path, issue_mapping, user_mapping
        )

        # 构建 HeteroData 对象
        data = HeteroData()
        data['user'].num_nodes = len(user_mapping)
        data['issue'].x = issue_x
        data['user'].x = user_embedding.weight
        data['user', 'participate', 'issue'].edge_index = edge_index
        data['user', 'participate', 'issue'].edge_weight = edge_weight
        data['issue'].is_open_issue = is_open_issue
        data['user'].num_nodes = len(user_mapping)
        # 添加正样本的边（user-resolve-issue）
        # 是否需要提前将正样本对应的索引从训练集中删除？
        # 可以分成两种情况讨论：
        # 1）给刚被打开的issue分配解决者：由于此时解决者是不会和issue有交互行为的，需要提前删掉正样本
        # 此时仅通过用户过去的交互行为来预测谁是解决者。更适合让模型挖掘出：参与者不一定是解决者的知识
        # 2）给一段时间后的issue分配解决者：由于此时解决者可能已经和issue有过一些交互行为，所以可以保留正样本。
        # 此时不仅通过用户过去的交互行为，还有与当前issue的交互行为预测谁是解决者。更适合让模型挖掘出：哪种行为的参与者更可能是解决者
        data['issue', 'resolved_by', 'user'].edge_index = pos_edge_index
        # pos_edge_label = torch.ones(pos_edge_index.size(1), device=pos_edge_index.device)
        # data['issue', 'resolved_by', 'user'].edge_label = pos_edge_label
        # 添加需要测试时预测的边
        data['user', 'open', 'issue'].edge_index = open_edge_index
        #根据需要从参与边中移除解决边
        self.remove_positive_edges_from_participate(data)
        #将图转换为无向图
        data = ToUndirected()(data)

        # 应用预处理转换
        if self.pre_transform:
            data = self.pre_transform(data)

        # 保存处理后的数据
        # torch.save(self.collate([data]), self.processed_paths[0])
        self.save([data], self.processed_paths[0])

        # 保存映射，供后续使用
        torch.save((user_mapping, issue_mapping), os.path.join(self.processed_dir, 'mappings.pt'))

    def get_node_mapping(self, file_path, index_col, encoders=None, cleaners=None):
        try:
            df = pd.read_csv(file_path, index_col=index_col)
        except Exception as e:
            print(f"Error reading the CSV file {file_path}: {e}")
            return None, None

        node_mapping = {index: i for i, index in enumerate(df.index.unique())}

        if cleaners:
            for col, cleaner in cleaners.items():
                df[col] = df[col].fillna('').apply(cleaner)

        node_vec = None
        if encoders:
            node_vec_list = []
            for col, encoder in encoders.items():
                encoded = encoder(df[col])
                node_vec_list.append(torch.tensor(encoded, dtype=torch.float))
            node_vec = torch.cat(node_vec_list, dim=-1) if node_vec_list else None

        return node_vec, node_mapping

    def get_edge_index(self, file_path, src_index_col, src_mapping,
                       dst_index_col, dst_mapping, weight_mapping=None, weight_col=None):
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading the CSV file {file_path}: {e}")
            return None, None, None

        # 映射源和目标节点到索引
        src = df[src_index_col].map(src_mapping)
        dst = df[dst_index_col].map(dst_mapping)

        # 删除缺失值
        valid = src.notna() & dst.notna()
        src = src[valid].astype(int).tolist()
        dst = dst[valid].astype(int).tolist()

        edge_index = torch.tensor([src, dst], dtype=torch.long)

        edge_attr = None  # 处理边的属性

        edge_weight = None
        if weight_mapping and weight_col:
            weights = df[weight_col].map(weight_mapping).fillna(0).tolist()
            edge_weight = torch.tensor(weights, dtype=torch.float)

        return edge_index, edge_attr, edge_weight

    def get_resolved_edges(self, file_path, issue_mapping, user_mapping):
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"Error reading the CSV file {file_path}: {e}")
            return None


        # 创建边的列表
        issue_indices = []
        user_indices = []
        df['resolver'] = df['resolver'].apply(self.extract_and_filter_resolvers)
        for _, row in df.iterrows():
            issue_idx = issue_mapping.get(row['number'], None)
            #print("issue_idx",issue_idx)
            if issue_idx is not None:
                for resolver in row['resolver']:
                    #print("resolver",resolver)
                    user_idx = user_mapping.get(resolver, None)
                    if user_idx is not None:
                        issue_indices.append(issue_idx)
                        user_indices.append(user_idx)

        resolved_edge_index = torch.tensor([issue_indices, user_indices], dtype=torch.long)
        return resolved_edge_index


    def extract_and_filter_resolvers(self,resolvers_str):
        resolvers = resolvers_str.strip("[]").split(',')
        filtered_resolvers  = [resolver.strip().strip("'") for resolver in resolvers]
        # filtered_resolvers = [resolver for resolver in resolvers if '[bot]' not in resolver]

        return filtered_resolvers


    def remove_positive_edges_from_participate(self,data):
        """
        从 'participate' 边中移除那些在 'resolved_by' 边中的边，防止信息泄露。
        """
        participate_edge_index = data['user', 'participate', 'issue'].edge_index
        resolved_edge_index = data['issue', 'resolved_by', 'user'].edge_index
        # 调整方向
        resolved_edge_index_adjusted = torch.flip(resolved_edge_index, [0])

        # 获取节点总数，用于计算唯一边 ID（利用乘积的基数和加法的独立性）
        num_users = data['user'].num_nodes
        num_issues = data['issue'].num_nodes
        max_node_index = max(num_users, num_issues)
        edge_ids_participate = participate_edge_index[0] * max_node_index + participate_edge_index[1]
        edge_ids_resolved = resolved_edge_index_adjusted[0] * max_node_index + resolved_edge_index_adjusted[1]

        # 找到需要移除的边（检查参与边中是否有解决边）
        mask = ~torch.isin(edge_ids_participate, edge_ids_resolved)

        # 过滤参与边
        filtered_participate_edge_index = participate_edge_index[:, mask]
        if 'edge_weight' in data['user', 'participate', 'issue']:
            filtered_edge_weight = data['user', 'participate', 'issue'].edge_weight[mask]
            data['user', 'participate', 'issue'].edge_weight = filtered_edge_weight
        data['user', 'participate', 'issue'].edge_index = filtered_participate_edge_index

def dataset_to_graph(dataset_name):
    print("load nodes and egdes from csv...")
    dataset = IssueAssignDataset(os.path.abspath(os.path.join('dataset',dataset_name)))
    data = dataset[0]
    user_mapping, issue_mapping = torch.load(os.path.join(dataset.processed_dir,'mappings.pt'))
    # num_users = data['user'].num_nodes
    # num_issues = data['issue'].num_nodes
    return data,user_mapping, issue_mapping