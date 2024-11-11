from torch_geometric.transforms import RandomLinkSplit
from torch_geometric.loader import LinkNeighborLoader
from torch_geometric.loader import NeighborLoader
import torch
# 将数据划分为训练集、验证集和测试集
# 使用 RandomLinkSplit 划分 'resolve' 边
def split_dataset(data):
    print("将数据划分为训练集、验证集------------------------------------------")
    dataset_split = RandomLinkSplit(
        num_val=0.1,
        num_test=0, # 测试集单独提供
        is_undirected=True,
        add_negative_train_samples=True,
        edge_types=[('issue', 'resolved_by', 'user')],
        rev_edge_types=[('user', 'rev_resolved_by', 'issue')]
    )
    train_data, val_data, _ = dataset_split(data)
    return train_data, val_data

def dataset_to_batch(data,train_data,val_data,batch_size):
      # 创建数据加载器
    num_neighbors=[10, 10] # 每层采样的邻居数，可以根据需要调整
    print("train_loader ---------------------------------")
    train_loader = LinkNeighborLoader(
        train_data,
        num_neighbors=num_neighbors, 
        edge_label_index=(('issue', 'resolved_by', 'user'),
        train_data['issue', 'resolved_by', 'user'].edge_label_index
        ),
        edge_label=train_data['issue', 'resolved_by', 'user'].edge_label,
        batch_size=batch_size,
        shuffle=True
    )
    print("val_loader ---------------------------------")
    val_loader = LinkNeighborLoader(
        val_data,
        num_neighbors=num_neighbors,
        edge_label_index=(('issue', 'resolved_by', 'user'),
        val_data['issue', 'resolved_by', 'user'].edge_label_index
        ),
        edge_label=val_data['issue', 'resolved_by', 'user'].edge_label,
        batch_size=batch_size,
        shuffle=False
    )
    print("test_loader ---------------------------------")
    # self.test_loader = LinkNeighborLoader(
    # self.test_data,
    # num_neighbors=num_neighbors,
    # edge_label_index=(('issue', 'resolved_by', 'user'),
    # self.test_data['issue', 'resolved_by', 'user'].edge_label_index
    # ),
    # edge_label=self.test_data['issue', 'resolved_by', 'user'].edge_label,
    # batch_size=batch_size,
    # shuffle=False
    # ) 
    
    # 获取 open_issues 的索引
    open_issue_indices = torch.nonzero(data['issue'].is_open_issue).squeeze()
    test_loader = NeighborLoader(
        data,
        num_neighbors=[0], # 关注最新的open_issue 不考虑邻居
        input_nodes=('issue', open_issue_indices), # 每次从data的open_issue_indices中选取batch_size个节点
        batch_size=data['user', 'open', 'issue'].edge_index.size(1), # 所有open_issue的数量
        shuffle=False
    )
    return train_loader,val_loader,test_loader
  




