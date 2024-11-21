// (function() {
//   console.log('Content script loaded');

//   // 检查当前页面是否是 Issue 页面
//   const isIssuePage = () => {
//     console.log('Checking if current page is an issue page');
//     return /^\/[^\/]+\/[^\/]+\/issues\/\d+$/.test(window.location.pathname);
//   };

//   console.log('Current pathname:', window.location.pathname);
//   console.log('Is issue page:', isIssuePage());

//   if (!isIssuePage()) {
//     console.log('Not an issue page');
//     return;
//   }

//   console.log('This is an issue page');

//   // 获取用户登录名
//   function getUserLogin() {
//     const meta = document.querySelector('meta[name="user-login"]');
//     if (meta) {
//       return meta.getAttribute('content');
//     } else {
//       return null;
//     }
//   }

//   // 定义一个函数，用于创建按钮和添加事件监听器
//   function addResolverButton() {
//     console.log('Adding resolver button');

//     // 创建按钮
//     const button = document.createElement('button');
//     button.innerText = '查看该 issue 的可能解决者';
//     button.style.marginLeft = '10px';
//     button.style.position = 'relative';
//     button.style.zIndex = '1000'; // 确保在最上面
//     button.classList.add('btn', 'btn-sm');

//     // 获取页面上的操作栏
//     const actionsBar = document.querySelector('.gh-header-actions');
//     if (actionsBar) {
//       console.log('Found actions bar');
//       actionsBar.appendChild(button);
//     } else {
//       console.log('Actions bar not found, trying header');
//       // 如果找不到操作栏，可以将按钮添加到标题后面
//       const header = document.querySelector('.gh-header-show');
//       if (header) {
//         header.appendChild(button);
//       } else {
//         console.log('Header not found');
//         return;
//       }
//     }

//     // 按钮点击事件
//     button.addEventListener('click', () => {
//       console.log('Button clicked');
//       // 获取仓库 owner、name 和 issue number
//       const pathParts = location.pathname.split('/');
//       const owner = pathParts[1];
//       const repo = pathParts[2];
//       const issueNumber = pathParts[4];

//       console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

//       // 构造请求数据
//       const requestData = {
//         owner: owner,
//         name: repo,
//         number: parseInt(issueNumber)
//       };

//       // 发送请求到后端 API
//       fetch('http://localhost:8000/get_issue_resolvers', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(requestData)
//       })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('Network response was not ok');
//         }
//         return response.json();
//       })
//       .then(data => {
//         // 处理返回的数据，显示在页面上
//         if (data && data.assignee && data.assignee.length > 0) {
//           showResolvers(data.assignee, data.probability, owner, repo, issueNumber);
//         } else {
//           alert('未找到可能的解决者。');
//         }
//       })
//       .catch(error => {
//         console.error('Error fetching issue resolvers:', error);
//         alert('获取可能的解决者时出错。');
//       });
//     });
//   }

//   function showResolvers(assignees, probabilities, owner, repo, issueNumber) {
//     console.log('Showing resolvers');
//     // 检查是否已存在结果容器，避免重复添加
//     let container = document.getElementById('issue-resolver-container');
//     if (container) {
//       container.remove();
//     }
  
//     // 创建结果容器
//     container = document.createElement('div');
//     container.id = 'issue-resolver-container';
//     // container.style.marginTop = '5px';
//     container.style.display = 'flex'; // 添加flex布局
//     container.style.alignItems = 'flex-start'; // 顶部对齐
//     // container.style.alignItems = 'center'; // 容器中的项目垂直居中
//     container.style.justifyContent = 'center'; // 水平居中
  
//     // 创建可能的解决者容器
//     const resolverContainer = document.createElement('div');
//     //resolverContainer.style.marginRight = '20px'; // 与反馈容器保持一定距离

//     const title = document.createElement('h3');
//     title.innerText = '可能的解决者：';
//     resolverContainer.appendChild(title);
  
//     const list = document.createElement('ul');
//     list.style.listStyleType = 'none';
//     resolverContainer.appendChild(list);
  
//     assignees.forEach((assignee, index) => {
//       const item = document.createElement('li');
//       item.style.marginBottom = '5px';
  
//       const link = document.createElement('a');
//       link.href = `https://github.com/${assignee}`;
//       link.target = '_blank';
//       link.innerText = assignee;
  
//       const probability = probabilities[index];
  
//       const probSpan = document.createElement('span');
//       probSpan.innerText = `（概率：${(probability * 100).toFixed(4)}%）`;
//       probSpan.style.marginLeft = '10px';
//       probSpan.style.color = '#888';
  
//       item.appendChild(link);
//       item.appendChild(probSpan);
//       list.appendChild(item);
//     });
  
//     // 将可能的解决者容器添加到主容器
//     container.appendChild(resolverContainer);
  
//     // 创建反馈容器
//     const feedbackContainer = document.createElement('div');
//     feedbackContainer.style.marginLeft = '5px'; // 与左侧保持一点距离
//     feedbackContainer.style.display = 'flex';
//     feedbackContainer.style.flexDirection = 'column';
//     feedbackContainer.style.alignItems = 'center';
  
//     const feedbackTitle = document.createElement('h3');
//     feedbackTitle.innerText = '这个结果对您是否有帮助：';
//     feedbackTitle.style.marginBottom = '10px';
//     feedbackContainer.appendChild(feedbackTitle);

//     const feedbackIcons = document.createElement('div'); // 创建一个新的div用于容纳图标
//     feedbackIcons.style.display = 'flex';
//     feedbackIcons.style.alignItems = 'center';
//     // feedbackIcons.style.justifyContent = 'space-around'; // 图标间有空间
  
//     const thumbsUp = document.createElement('span');
//     thumbsUp.innerText = '👍';
//     thumbsUp.style.cursor = 'pointer';
//     thumbsUp.style.fontSize = '28px';
//     // thumbsUp.style.marginBottom = '20px';
//     thumbsUp.style.marginRight = '30px'; // 增加间隔至30px

//     feedbackIcons.appendChild(thumbsUp);
  
//     const thumbsDown = document.createElement('span');
//     thumbsDown.innerText = '👎';
//     thumbsDown.style.cursor = 'pointer';
//     thumbsDown.style.fontSize = '28px';
//     feedbackIcons.appendChild(thumbsDown);

//     feedbackContainer.appendChild(feedbackIcons); // 将图标容器添加到反馈容器
  
//     // 将反馈容器添加到主容器
//     container.appendChild(feedbackContainer);
  
//     // 将结果容器添加到页面上
//     const discussionTimeline = document.querySelector('.js-discussion');
//     if (discussionTimeline) {
//       discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
//     } else {
//       // 如果找不到合适的位置，可以添加到标题后面
//       const header = document.querySelector('.gh-header');
//       if (header) {
//         header.parentNode.insertBefore(container, header.nextSibling);
//       }
//     }
  
//     // 添加反馈功能
//     let feedbackGiven = false;
  
//     thumbsUp.addEventListener('click', () => {
//       if (feedbackGiven) return;
//       feedbackGiven = true;
  
//       thumbsUp.style.color = 'green';
//       thumbsDown.style.color = '';
  
//       const userLogin = getUserLogin();
//       if (!userLogin) {
//         alert('无法获取您的用户名，请确保您已登录。');
//         return;
//       }
  
//       // 发送反馈到后端
//       const feedbackData = {
//         user: userLogin,
//         feedback: 'thumbs_up',
//         owner: owner,
//         name: repo,
//         number: parseInt(issueNumber)
//       };
  
//       fetch('http://localhost:8000/submit_feedback', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(feedbackData)
//       })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('网络响应失败');
//         }
//         return response.json();
//       })
//       .then(data => {
//         alert('感谢您的反馈！');
//       })
//       .catch(error => {
//         console.error('提交反馈时出错:', error);
//         alert('提交反馈时出错。');
//       });
//     });
  
//     thumbsDown.addEventListener('click', () => {
//       if (feedbackGiven) return;
//       feedbackGiven = true;
  
//       thumbsDown.style.color = 'red';
//       thumbsUp.style.color = '';
  
//       const userLogin = getUserLogin();
//       if (!userLogin) {
//         alert('无法获取您的用户名，请确保您已登录。');
//         return;
//       }
  
//       // 发送反馈到后端
//       const feedbackData = {
//         user: userLogin,
//         feedback: 'thumbs_down',
//         owner: owner,
//         name: repo,
//         number: parseInt(issueNumber)
//       };
  
//       fetch('http://localhost:8000/submit_feedback', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(feedbackData)
//       })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('网络响应失败');
//         }
//         return response.json();
//       })
//       .then(data => {
//         alert('感谢您的反馈！');
//       })
//       .catch(error => {
//         console.error('提交反馈时出错:', error);
//         alert('提交反馈时出错。');
//       });
//     });
//   }
  
//   // 等待页面完全加载后执行
//   if (document.readyState === 'complete' || document.readyState === 'interactive') {
//     console.log('Document ready, adding button');
//     addResolverButton();
//   } else {
//     console.log('Document not ready, adding event listener');
//     document.addEventListener('DOMContentLoaded', addResolverButton);
//   }
// })();


// (function() {
//   console.log('Content script loaded');

//   // 检查当前页面是否是 Issue 页面
//   const isIssuePage = () => {
//     console.log('Checking if current page is an issue page');
//     return /^\/[^\/]+\/[^\/]+\/issues\/\d+$/.test(window.location.pathname);
//   };

//   console.log('Current pathname:', window.location.pathname);
//   console.log('Is issue page:', isIssuePage());

//   if (!isIssuePage()) {
//     console.log('Not an issue page');
//     return;
//   }

//   console.log('This is an issue page');

//   // 定义一个函数，用于创建按钮和添加事件监听器
//   function addResolverButton() {
//     console.log('Adding resolver button');

//     // 创建按钮
//     const button = document.createElement('button');
//     button.innerText = '查看该 issue 的可能解决者';
//     button.style.marginLeft = '10px';
//     button.style.position = 'relative';
//     button.style.zIndex = '1000'; // 确保在最上面
//     button.classList.add('btn', 'btn-sm');

//     // 获取页面上的操作栏
//     const actionsBar = document.querySelector('.gh-header-actions');
//     if (actionsBar) {
//       console.log('Found actions bar');
//       actionsBar.appendChild(button);
//     } else {
//       console.log('Actions bar not found, trying header');
//       // 如果找不到操作栏，可以将按钮添加到标题后面
//       const header = document.querySelector('.gh-header-show');
//       if (header) {
//         header.appendChild(button);
//       } else {
//         console.log('Header not found');
//         return;
//       }
//     }

//     // 按钮点击事件
//     button.addEventListener('click', () => {
//       console.log('Button clicked');
//       // 获取仓库 owner、name 和 issue number
//       const pathParts = location.pathname.split('/');
//       const owner = pathParts[1];
//       const repo = pathParts[2];
//       const issueNumber = pathParts[4];

//       console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

//       // 构造请求数据
//       const requestData = {
//         owner: owner,
//         name: repo,
//         number: parseInt(issueNumber)
//       };

//       // 发送请求到后端 API
//       fetch('http://localhost:8000/get_issue_resolvers', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(requestData)
//       })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('Network response was not ok');
//         }
//         return response.json();
//       })
//       .then(data => {
//         // 处理返回的数据，显示在页面上
//         if (data && data.assignee && data.assignee.length > 0) {
//           showResolvers(data.assignee, data.probability);
//         } else {
//           alert('未找到可能的解决者。');
//         }
//       })
//       .catch(error => {
//         console.error('Error fetching issue resolvers:', error);
//         alert('获取可能的解决者时出错。');
//       });
//     });
//   }

//   // 显示可能的解决者
//   function showResolvers(assignees, probabilities) {
//     console.log('Showing resolvers');
//     // 检查是否已存在结果容器，避免重复添加
//     let container = document.getElementById('issue-resolver-container');
//     if (container) {
//       container.remove();
//     }

//     // 创建结果容器
//     container = document.createElement('div');
//     container.id = 'issue-resolver-container';
//     container.style.marginTop = '20px';

//     const title = document.createElement('h3');
//     title.innerText = '可能的解决者：';
//     container.appendChild(title);

//     const list = document.createElement('ul');
//     list.style.listStyleType = 'none';
//     container.appendChild(list);

//     assignees.forEach((assignee, index) => {
//       const item = document.createElement('li');
//       item.style.marginBottom = '5px';

//       const link = document.createElement('a');
//       link.href = `https://github.com/${assignee}`;
//       link.target = '_blank';
//       link.innerText = assignee;

//       const probability = probabilities[index];

//       const probSpan = document.createElement('span');
//       probSpan.innerText = `（概率：${(probability * 100).toFixed(4)}%）`;
//       probSpan.style.marginLeft = '10px';
//       probSpan.style.color = '#888';

//       item.appendChild(link);
//       item.appendChild(probSpan);
//       list.appendChild(item);
//     });

//     // 将结果容器添加到页面上
//     const discussionTimeline = document.querySelector('.js-discussion');
//     if (discussionTimeline) {
//       discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
//     } else {
//       // 如果找不到合适的位置，可以添加到标题后面
//       const header = document.querySelector('.gh-header');
//       if (header) {
//         header.parentNode.insertBefore(container, header.nextSibling);
//       }
//     }
//   }

//   // 等待页面完全加载后执行
//   if (document.readyState === 'complete' || document.readyState === 'interactive') {
//     console.log('Document ready, adding button');
//     addResolverButton();
//   } else {
//     console.log('Document not ready, adding event listener');
//     document.addEventListener('DOMContentLoaded', addResolverButton);
//   }
// })();


// content_script.js

// (function() {
//   console.log('Content script loaded');

//   // 上一次处理的 URL
//   let lastUrl = location.href;

//   // 检查当前页面是否是 Issue 页面
//   function isIssuePage() {
//     return /^\/[^\/]+\/[^\/]+\/issues\/\d+$/.test(location.pathname);
//   }

//   // 添加按钮和事件监听器
//   function addResolverButton() {
//     // 检查按钮是否已经存在，避免重复添加
//     if (document.getElementById('issue-resolver-button')) {
//       return;
//     }

//     // 创建按钮
//     const button = document.createElement('button');
//     button.id = 'issue-resolver-button';
//     button.innerText = '查看该 issue 的可能解决者';
//     button.style.marginLeft = '10px';
//     button.classList.add('btn', 'btn-sm');

//     // 获取页面上的操作栏
//     const actionsBar = document.querySelector('.gh-header-actions');
//     if (actionsBar) {
//       actionsBar.appendChild(button);
//     } else {
//       // 如果找不到操作栏，退出函数
//       return;
//     }

//     // 按钮点击事件
//     button.addEventListener('click', () => {
//       // 获取仓库 owner、name 和 issue number
//       const pathParts = location.pathname.split('/');
//       const owner = pathParts[1];
//       const repo = pathParts[2];
//       const issueNumber = pathParts[4];

//       // 构造请求数据
//       const requestData = {
//         owner: owner,
//         name: repo,
//         number: parseInt(issueNumber)
//       };

//       // 发送请求到后端 API
//       fetch('http://localhost:8000/get_issue_resolvers', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(requestData)
//       })
//       .then(response => {
//         if (!response.ok) {
//           throw new Error('Network response was not ok');
//         }
//         return response.json();
//       })
//       .then(data => {
//         // 处理返回的数据，显示在页面上
//         if (data && data.assignee && data.assignee.length > 0) {
//           showResolvers(data.assignee, data.probability);
//         } else {
//           alert('未找到可能的解决者。');
//         }
//       })
//       .catch(error => {
//         console.error('Error fetching issue resolvers:', error);
//         alert('获取可能的解决者时出错。');
//       });
//     });
//   }

//   // 显示可能的解决者
//   function showResolvers(assignees, probabilities) {
//     // 检查是否已存在结果容器，避免重复添加
//     let container = document.getElementById('issue-resolver-container');
//     if (container) {
//       container.remove();
//     }

//     // 创建结果容器
//     container = document.createElement('div');
//     container.id = 'issue-resolver-container';
//     container.style.marginTop = '20px';

//     const title = document.createElement('h3');
//     title.innerText = '可能的解决者：';
//     container.appendChild(title);

//     const list = document.createElement('ul');
//     list.style.listStyleType = 'none';
//     container.appendChild(list);

//     assignees.forEach((assignee, index) => {
//       const item = document.createElement('li');
//       item.style.marginBottom = '5px';

//       const link = document.createElement('a');
//       link.href = `https://github.com/${assignee}`;
//       link.target = '_blank';
//       link.innerText = assignee;

//       const probability = probabilities[index];

//       const probSpan = document.createElement('span');
//       probSpan.innerText = `（概率：${(probability * 100).toFixed(4)}%）`;
//       probSpan.style.marginLeft = '10px';
//       probSpan.style.color = '#888';

//       item.appendChild(link);
//       item.appendChild(probSpan);
//       list.appendChild(item);
//     });

//     // 将结果容器添加到页面上
//     const discussionTimeline = document.querySelector('.js-discussion');
//     if (discussionTimeline) {
//       discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
//     } else {
//       // 如果找不到合适的位置，可以添加到标题后面
//       const header = document.querySelector('.gh-header');
//       if (header) {
//         header.parentNode.insertBefore(container, header.nextSibling);
//       }
//     }
//   }

//   // 初始化函数
//   function init() {
//     if (isIssuePage()) {
//       console.log('Initializing on issue page');
//       addResolverButton();
//     }
//   }

//   // 监听 DOM 和 URL 变化
//   const observer = new MutationObserver(() => {
//     if (location.href !== lastUrl) {
//       console.log('URL changed:', location.href);
//       lastUrl = location.href;
//       init();
//     }
//   });

//   observer.observe(document.body, { childList: true, subtree: true });

//   // 初始执行
//   init();
// })();

// content_script.js

(function() {
  console.log('Content script loaded');

  // 检查当前页面是否是 Issue 页面
  const isIssuePage = () => {
    console.log('Checking if current page is an issue page');
    return /^\/[^\/]+\/[^\/]+\/issues\/\d+$/.test(window.location.pathname);
  };

  console.log('Current pathname:', window.location.pathname);
  console.log('Is issue page:', isIssuePage());

  if (!isIssuePage()) {
    console.log('Not an issue page');
    return;
  }

  console.log('This is an issue page');

  // 获取用户登录名
  function getUserLogin() {
    const meta = document.querySelector('meta[name="user-login"]');
    if (meta) {
      return meta.getAttribute('content');
    } else {
      return null;
    }
  }

  // 定义一个函数，用于创建按钮和添加事件监听器
  function addResolverButton() {
    console.log('Adding resolver button');

    // 创建按钮
    const button = document.createElement('button');
    button.innerText = '查看该 issue 的可能解决者';
    button.style.marginLeft = '10px';
    button.style.position = 'relative';
    button.style.zIndex = '1000'; // 确保在最上面
    button.classList.add('btn', 'btn-sm');

    // 获取页面上的操作栏
    const actionsBar = document.querySelector('.gh-header-actions');
    if (actionsBar) {
      console.log('Found actions bar');
      actionsBar.appendChild(button);
    } else {
      console.log('Actions bar not found, trying header');
      // 如果找不到操作栏，可以将按钮添加到标题后面
      const header = document.querySelector('.gh-header-show');
      if (header) {
        header.appendChild(button);
      } else {
        console.log('Header not found');
        return;
      }
    }

    // 按钮点击事件
    button.addEventListener('click', () => {
      console.log('Button clicked');
      // 获取仓库 owner、name 和 issue number
      const pathParts = location.pathname.split('/');
      const owner = pathParts[1];
      const repo = pathParts[2];
      const issueNumber = pathParts[4];

      console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

      // 构造请求数据
      const requestData = {
        owner: owner,
        name: repo,
        number: parseInt(issueNumber)
      };

      // 发送请求到后端 API
      fetch('http://localhost:8000/get_issue_resolvers', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // 处理返回的数据，显示在页面上
        if (data && data.recommendations && data.recommendations.length > 0) {
          showResolvers(data.recommendations, owner, repo, issueNumber);
        } else {
          alert('未找到可能的解决者。');
        }
      })
      .catch(error => {
        console.error('Error fetching issue resolvers:', error);
        alert('获取可能的解决者时出错。');
      });
    });
  }

  function showResolvers(recommendations, owner, repo, issueNumber) {
    console.log('Showing resolvers');
    // 检查是否已存在结果容器，避免重复添加
    let container = document.getElementById('issue-resolver-container');
    if (container) {
      container.remove();
    }

    // 创建结果容器
    container = document.createElement('div');
    container.id = 'issue-resolver-container';
    container.style.marginTop = '20px';

    // 创建模型选择下拉框
    const modelSelector = document.createElement('select');
    modelSelector.style.marginBottom = '10px';
    modelSelector.style.padding = '5px';

    recommendations.forEach((rec, index) => {
      const option = document.createElement('option');
      option.value = index;
      option.text = rec.model;
      modelSelector.appendChild(option);
    });

    container.appendChild(modelSelector);

    // 创建显示区域
    const displayArea = document.createElement('div');
    container.appendChild(displayArea);

    // 监听模型选择变化
    modelSelector.addEventListener('change', () => {
      const selectedIndex = modelSelector.value;
      displayRecommendation(recommendations[selectedIndex], owner, repo, issueNumber);
    });

    // 默认显示第一个模型的推荐结果
    displayRecommendation(recommendations[0], owner, repo, issueNumber);

    // 将结果容器添加到页面上
    const discussionTimeline = document.querySelector('.js-discussion');
    if (discussionTimeline) {
      discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
    } else {
      // 如果找不到合适的位置，可以添加到标题后面
      const header = document.querySelector('.gh-header');
      if (header) {
        header.parentNode.insertBefore(container, header.nextSibling);
      }
    }
  }

  function displayRecommendation(recommendation, owner, repo, issueNumber) {
    const displayArea = document.querySelector('#issue-resolver-container > div');
    if (!displayArea) return;

    // 清空显示区域
    displayArea.innerHTML = '';

    // 创建标题和反馈容器
    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';

    // 创建可能的解决者容器
    const resolverContainer = document.createElement('div');

    const title = document.createElement('h3');
    title.innerText = `模型：${recommendation.model}`;
    resolverContainer.appendChild(title);

    const list = document.createElement('ul');
    list.style.listStyleType = 'none';
    resolverContainer.appendChild(list);

    recommendation.assignee.forEach((assignee, index) => {
      const item = document.createElement('li');
      item.style.marginBottom = '5px';

      const link = document.createElement('a');
      link.href = `https://github.com/${assignee}`;
      link.target = '_blank';
      link.innerText = assignee;

      const probability = recommendation.probability[index];

      const probSpan = document.createElement('span');
      probSpan.innerText = `（概率：${(probability * 100).toFixed(4)}%）`;
      probSpan.style.marginLeft = '10px';
      probSpan.style.color = '#888';

      item.appendChild(link);
      item.appendChild(probSpan);
      list.appendChild(item);
    });

    // 创建反馈容器
    const feedbackContainer = document.createElement('div');
    feedbackContainer.style.marginLeft = '20px';
    feedbackContainer.style.display = 'flex';
    feedbackContainer.style.flexDirection = 'column';
    feedbackContainer.style.alignItems = 'center';

    const feedbackTitle = document.createElement('h3');
    feedbackTitle.innerText = '这个结果对您是否有帮助：';
    feedbackTitle.style.marginBottom = '10px';
    feedbackContainer.appendChild(feedbackTitle);

    const feedbackIcons = document.createElement('div');
    feedbackIcons.style.display = 'flex';
    feedbackIcons.style.alignItems = 'center';

    const thumbsUp = document.createElement('span');
    thumbsUp.innerText = '👍';
    thumbsUp.style.cursor = 'pointer';
    thumbsUp.style.fontSize = '28px';
    thumbsUp.style.marginRight = '30px';

    feedbackIcons.appendChild(thumbsUp);

    const thumbsDown = document.createElement('span');
    thumbsDown.innerText = '👎';
    thumbsDown.style.cursor = 'pointer';
    thumbsDown.style.fontSize = '28px';
    feedbackIcons.appendChild(thumbsDown);

    feedbackContainer.appendChild(feedbackIcons);

    // 将可能的解决者容器和反馈容器添加到主容器
    container.appendChild(resolverContainer);
    container.appendChild(feedbackContainer);

    // 将主容器添加到显示区域
    displayArea.appendChild(container);

    // 添加反馈功能
    let feedbackGiven = false;

    thumbsUp.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsUp.style.color = 'green';
      thumbsDown.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('无法获取您的用户名，请确保您已登录。');
        return;
      }

      // 发送反馈到后端
      const feedbackData = {
        user: userLogin,
        feedback: 'thumbs_up',
        owner: owner,
        name: repo,
        number: parseInt(issueNumber),
        model: recommendation.model
      };

      fetch('http://localhost:8000/submit_feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('网络响应失败');
        }
        return response.json();
      })
      .then(data => {
        alert('感谢您的反馈！');
      })
      .catch(error => {
        console.error('提交反馈时出错:', error);
        alert('提交反馈时出错。');
      });
    });

    thumbsDown.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsDown.style.color = 'red';
      thumbsUp.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('无法获取您的用户名，请确保您已登录。');
        return;
      }

      // 发送反馈到后端
      const feedbackData = {
        user: userLogin,
        feedback: 'thumbs_down',
        owner: owner,
        name: repo,
        number: parseInt(issueNumber),
        model: recommendation.model
      };

      fetch('http://localhost:8000/submit_feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('网络响应失败');
        }
        return response.json();
      })
      .then(data => {
        alert('感谢您的反馈！');
      })
      .catch(error => {
        console.error('提交反馈时出错:', error);
        alert('提交反馈时出错。');
      });
    });
  }

  // 等待页面完全加载后执行
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document ready, adding button');
    addResolverButton();
  } else {
    console.log('Document not ready, adding event listener');
    document.addEventListener('DOMContentLoaded', addResolverButton);
  }
})();


