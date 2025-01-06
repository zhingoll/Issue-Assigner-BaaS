(function() {
  console.log('Content script loaded');

  // Check if the current page is an Issue page
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

  // Get user login name
  function getUserLogin() {
    const meta = document.querySelector('meta[name="user-login"]');
    if (meta) {
      return meta.getAttribute('content');
    } else {
      return null;
    }
  }

  // Define a function to create a button and add event listeners
  function addResolverButton() {
    console.log('Adding resolver button');

    const button = document.createElement('button');
    button.innerText = 'View possible resolvers for this issue';
    button.style.marginLeft = '10px';
    button.style.position = 'relative';
    button.style.zIndex = '1000'; 
    button.classList.add('btn', 'btn-sm');

    // Get the action bar on the page
    const actionsBar = document.querySelector('.gh-header-actions');
    if (actionsBar) {
      console.log('Found actions bar');
      actionsBar.appendChild(button);
    } else {
      console.log('Actions bar not found, trying header');
      // If action bar is not found, try adding the button next to the header
      const header = document.querySelector('.gh-header-show');
      if (header) {
        header.appendChild(button);
      } else {
        console.log('Header not found');
        return;
      }
    }

    // Button click event
    button.addEventListener('click', () => {
      console.log('Button clicked');
      // Get repository owner, name, and issue number
      const pathParts = location.pathname.split('/');
      const owner = pathParts[1];
      const repo = pathParts[2];
      const issueNumber = pathParts[4];

      console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

      // Construct request data
      const requestData = {
        owner: owner,
        name: repo,
        number: parseInt(issueNumber)
      };

      // Send request to backend API
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
        // Process the returned data and display on the page
        if (data && data.recommendations && data.recommendations.length > 0) {
          showResolvers(data.recommendations, owner, repo, issueNumber);
        } else {
          alert('No possible resolvers found.');
        }
      })
      .catch(error => {
        console.error('Error fetching issue resolvers:', error);
        alert('Error fetching possible resolvers.');
      });
    });
  }

  function showResolvers(recommendations, owner, repo, issueNumber) {
    console.log('Showing resolvers');
    // Check if a result container already exists to avoid duplication
    let container = document.getElementById('issue-resolver-container');
    if (container) {
      container.remove();
    }

    // Create result container
    container = document.createElement('div');
    container.id = 'issue-resolver-container';
    container.style.marginTop = '20px';

    // Create model selection dropdown
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

    // Create display area
    const displayArea = document.createElement('div');
    container.appendChild(displayArea);

    // Listen to model selection changes
    modelSelector.addEventListener('change', () => {
      const selectedIndex = modelSelector.value;
      displayRecommendation(recommendations[selectedIndex], owner, repo, issueNumber);
    });

    // Default display the first model's recommendations
    displayRecommendation(recommendations[0], owner, repo, issueNumber);

    // Add result container to the page
    const discussionTimeline = document.querySelector('.js-discussion');
    if (discussionTimeline) {
      discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
    } else {
      // If no suitable place is found, try adding it next to the header
      const header = document.querySelector('.gh-header');
      if (header) {
        header.parentNode.insertBefore(container, header.nextSibling);
      }
    }
  }

  function displayRecommendation(recommendation, owner, repo, issueNumber) {
    const displayArea = document.querySelector('#issue-resolver-container > div');
    if (!displayArea) return;

    // Clear display area
    displayArea.innerHTML = '';

    // Create title and feedback containers
    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';

    // Create possible resolvers container
    const resolverContainer = document.createElement('div');

    const title = document.createElement('h3');
    title.innerText = `Model:${recommendation.model}`;
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
      probSpan.innerText = `(Probability:${(probability * 100).toFixed(4)}%)`;
      probSpan.style.marginLeft = '10px';
      probSpan.style.color = '#888';

      item.appendChild(link);
      item.appendChild(probSpan);
      list.appendChild(item);
    });

    // Create feedback container
    const feedbackContainer = document.createElement('div');
    feedbackContainer.style.marginLeft = '20px';
    feedbackContainer.style.display = 'flex';
    feedbackContainer.style.flexDirection = 'column';
    feedbackContainer.style.alignItems = 'center';

    const feedbackTitle = document.createElement('h3');
    feedbackTitle.innerText = 'Was this result helpful to you?';
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

    // Add possible resolvers container and feedback container to the main container
    container.appendChild(resolverContainer);
    container.appendChild(feedbackContainer);

    // Add main container to the display area
    displayArea.appendChild(container);

    // Add feedback functionality
    let feedbackGiven = false;

    thumbsUp.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsUp.style.color = 'green';
      thumbsDown.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

      // Send feedback to the backend
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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    thumbsDown.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsDown.style.color = 'red';
      thumbsUp.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

      // Send feedback to the backend
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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });
  }

  // Execute after the page is fully loaded
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document ready, adding button');
    addResolverButton();
  } else {
    console.log('Document not ready, adding event listener');
    document.addEventListener('DOMContentLoaded', addResolverButton);
  }
})();


(function() {
  console.log('Content script loaded');

  // Check if the current page is an Issue page
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

  // Get user login name
  function getUserLogin() {
    const meta = document.querySelector('meta[name="user-login"]');
    if (meta) {
      return meta.getAttribute('content');
    } else {
      return null;
    }
  }

  // Define a function to create a button and add event listeners
  function addResolverButton() {
    console.log('Adding resolver button');

    const button = document.createElement('button');
    button.innerText = 'View possible resolvers for this issue';
    button.style.marginLeft = '10px';
    button.style.position = 'relative';
    button.style.zIndex = '1000'; 
    button.classList.add('btn', 'btn-sm');

    // Get the action bar on the page
    const actionsBar = document.querySelector('.gh-header-actions');
    if (actionsBar) {
      console.log('Found actions bar');
      actionsBar.appendChild(button);
    } else {
      console.log('Actions bar not found, trying header');
      const header = document.querySelector('.gh-header-show');
      if (header) {
        header.appendChild(button);
      } else {
        console.log('Header not found');
        return;
      }
    }

    // Button click event
    button.addEventListener('click', () => {
      console.log('Button clicked');
      // Get repository owner, name, and issue number
      const pathParts = location.pathname.split('/');
      const owner = pathParts[1];
      const repo = pathParts[2];
      const issueNumber = pathParts[4];

      console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

      // Construct request data
      const requestData = {
        owner: owner,
        name: repo,
        number: parseInt(issueNumber)
      };

      // Send request to backend API
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
        // Process the returned data and display on the page
        if (data && data.recommendations && data.recommendations.length > 0) {
          showResolvers(data.recommendations, owner, repo, issueNumber);
        } else {
          alert('No possible resolvers found.');
        }
      })
      .catch(error => {
        console.error('Error fetching issue resolvers:', error);
        alert('Error fetching possible resolvers.');
      });
    });
  }

  function showResolvers(recommendations, owner, repo, issueNumber) {
    console.log('Showing resolvers');
    let container = document.getElementById('issue-resolver-container');
    if (container) {
      container.remove();
    }

    container = document.createElement('div');
    container.id = 'issue-resolver-container';
    container.style.marginTop = '20px';

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

    const displayArea = document.createElement('div');
    container.appendChild(displayArea);

    modelSelector.addEventListener('change', () => {
      const selectedIndex = modelSelector.value;
      displayRecommendation(recommendations[selectedIndex], owner, repo, issueNumber);
    });

    // Default display the first model's recommendations
    displayRecommendation(recommendations[0], owner, repo, issueNumber);

    const discussionTimeline = document.querySelector('.js-discussion');
    if (discussionTimeline) {
      discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
    } else {
      const header = document.querySelector('.gh-header');
      if (header) {
        header.parentNode.insertBefore(container, header.nextSibling);
      }
    }
  }

  function displayRecommendation(recommendation, owner, repo, issueNumber) {
    const displayArea = document.querySelector('#issue-resolver-container > div');
    if (!displayArea) return;

    displayArea.innerHTML = '';

    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';

    const resolverContainer = document.createElement('div');

    const title = document.createElement('h3');
    title.innerText = `Model:${recommendation.model}`;
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
      probSpan.innerText = `(Probability:${(probability * 100).toFixed(4)}%)`;
      probSpan.style.marginLeft = '10px';
      probSpan.style.color = '#888';

      item.appendChild(link);
      item.appendChild(probSpan);
      list.appendChild(item);
    });

    container.appendChild(resolverContainer);

    // Feedback Container
    const feedbackContainer = document.createElement('div');
    feedbackContainer.style.marginLeft = '20px';
    feedbackContainer.style.display = 'flex';
    feedbackContainer.style.flexDirection = 'column';
    feedbackContainer.style.alignItems = 'center';

    const feedbackTitle = document.createElement('h3');
    feedbackTitle.innerText = 'Was this result helpful to you?';
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

    container.appendChild(feedbackContainer);

    displayArea.appendChild(container);

    // Add feedback functionality
    let feedbackGiven = false;
    thumbsUp.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsUp.style.color = 'green';
      thumbsDown.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    thumbsDown.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsDown.style.color = 'red';
      thumbsUp.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    // 在这里获取开发者的统计数据，并展示为堆叠条形图
    fetch('http://localhost:8000/get_developer_stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        owner: owner,
        name: repo,
        developers: recommendation.assignee
      })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch developer stats');
      return res.json();
    })
    .then(statsData => {
      // 创建一个显示区用于堆叠条形图
      const chartContainer = document.createElement('div');
      chartContainer.style.marginTop = '20px';

      // 指标按照 global_openrank, community_openrank, avg_activity, avg_response_time 的顺序堆叠
      // 可以根据需要调整颜色和顺序
      const metrics = [
        {key:'global_openrank', color:'#4CAF50', label:'Global OpenRank'},
        {key:'community_openrank', color:'#2196F3', label:'Community OpenRank'},
        {key:'avg_activity', color:'#FF9800', label:'Avg Activity'},
        {key:'avg_response_time', color:'#f44336', label:'Avg Response Time'}
      ];

      // 为每个开发者创建条形图
      recommendation.assignee.forEach(assignee => {
        const devData = statsData.find(d => d.developer === assignee);
        if (!devData) return;

        const barContainer = document.createElement('div');
        barContainer.style.display = 'flex';
        barContainer.style.alignItems = 'center';
        barContainer.style.marginBottom = '5px';

        const nameSpan = document.createElement('span');
        nameSpan.innerText = assignee + ': ';
        nameSpan.style.width = '100px';
        barContainer.appendChild(nameSpan);

        const total = metrics.reduce((sum,m)=> sum + (devData[m.key] || 0), 0);

        const barWrapper = document.createElement('div');
        barWrapper.style.display = 'flex';
        barWrapper.style.width = '300px';
        barWrapper.style.height = '20px';
        barWrapper.style.background = '#eee';
        barWrapper.style.position = 'relative';
        barWrapper.style.marginRight = '10px';

        metrics.forEach(m => {
          const val = devData[m.key] || 0;
          const fraction = total === 0 ? 0 : (val/total)*100;
          const seg = document.createElement('div');
          seg.style.width = fraction+'%';
          seg.style.background = m.color;
          seg.title = `${m.label}: ${val.toFixed(2)}`;
          barWrapper.appendChild(seg);
        });

        barContainer.appendChild(barWrapper);

        // 在条形图后面显示各指标简写及颜色图例（可选）
        const legend = document.createElement('span');
        legend.innerText = metrics.map(m => m.label).join(' | ');
        legend.style.fontSize = '12px';
        legend.style.color = '#555';

        barContainer.appendChild(legend);

        chartContainer.appendChild(barContainer);
      });

      displayArea.appendChild(chartContainer);
    })
    .catch(err => {
      console.error('Error fetching developer stats:', err);
    });

  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document ready, adding button');
    addResolverButton();
  } else {
    console.log('Document not ready, adding event listener');
    document.addEventListener('DOMContentLoaded', addResolverButton);
  }

})();



(function() {
  console.log('Content script loaded');

  // 检查是否为Issue页面
  const isIssuePage = () => {
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

  // 添加按钮
  function addResolverButton() {
    console.log('Adding resolver button');

    const button = document.createElement('button');
    button.innerText = 'View possible resolvers for this issue';
    button.style.marginLeft = '10px';
    button.style.position = 'relative';
    button.style.zIndex = '1000'; 
    button.classList.add('btn', 'btn-sm');

    const actionsBar = document.querySelector('.gh-header-actions');
    if (actionsBar) {
      console.log('Found actions bar');
      actionsBar.appendChild(button);
    } else {
      console.log('Actions bar not found, trying header');
      const header = document.querySelector('.gh-header-show');
      if (header) {
        header.appendChild(button);
      } else {
        console.log('Header not found');
        return;
      }
    }

    button.addEventListener('click', () => {
      console.log('Button clicked');
      const pathParts = location.pathname.split('/');
      const owner = pathParts[1];
      const repo = pathParts[2];
      const issueNumber = pathParts[4];

      console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

      const requestData = {
        owner: owner,
        name: repo,
        number: parseInt(issueNumber)
      };

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
        if (data && data.recommendations && data.recommendations.length > 0) {
          showResolvers(data.recommendations, owner, repo, issueNumber);
        } else {
          alert('No possible resolvers found.');
        }
      })
      .catch(error => {
        console.error('Error fetching issue resolvers:', error);
        alert('Error fetching possible resolvers.');
      });
    });
  }

  function showResolvers(recommendations, owner, repo, issueNumber) {
    console.log('Showing resolvers');
    let container = document.getElementById('issue-resolver-container');
    if (container) {
      container.remove();
    }

    container = document.createElement('div');
    container.id = 'issue-resolver-container';
    container.style.marginTop = '20px';

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

    const displayArea = document.createElement('div');
    container.appendChild(displayArea);

    modelSelector.addEventListener('change', () => {
      const selectedIndex = modelSelector.value;
      displayRecommendation(recommendations[selectedIndex], owner, repo, issueNumber);
    });

    // 默认显示第一个模型的结果
    displayRecommendation(recommendations[0], owner, repo, issueNumber);

    const discussionTimeline = document.querySelector('.js-discussion');
    if (discussionTimeline) {
      discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
    } else {
      const header = document.querySelector('.gh-header');
      if (header) {
        header.parentNode.insertBefore(container, header.nextSibling);
      }
    }
  }

  function displayRecommendation(recommendation, owner, repo, issueNumber) {
    const displayArea = document.querySelector('#issue-resolver-container > div');
    if (!displayArea) return;

    displayArea.innerHTML = '';

    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';

    const resolverContainer = document.createElement('div');

    const title = document.createElement('h3');
    title.innerText = `Model: ${recommendation.model}`;
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
      probSpan.innerText = `(Probability:${(probability * 100).toFixed(4)}%)`;
      probSpan.style.marginLeft = '10px';
      probSpan.style.color = '#888';

      item.appendChild(link);
      item.appendChild(probSpan);
      list.appendChild(item);
    });

    container.appendChild(resolverContainer);

    // Feedback Container
    const feedbackContainer = document.createElement('div');
    feedbackContainer.style.marginLeft = '20px';
    feedbackContainer.style.display = 'flex';
    feedbackContainer.style.flexDirection = 'column';
    feedbackContainer.style.alignItems = 'center';

    const feedbackTitle = document.createElement('h3');
    feedbackTitle.innerText = 'Was this result helpful to you?';
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

    container.appendChild(feedbackContainer);

    displayArea.appendChild(container);

    let feedbackGiven = false;
    thumbsUp.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsUp.style.color = 'green';
      thumbsDown.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    thumbsDown.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsDown.style.color = 'red';
      thumbsUp.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    // 获取开发者的统计数据并展示为堆叠条形图（仅global_openrank、community_openrank、avg_activity）
    fetch('http://localhost:8000/get_developer_stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        owner: owner,
        name: repo,
        developers: recommendation.assignee
      })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch developer stats');
      return res.json();
    })
    .then(statsData => {
      const metrics = [
        {key:'global_openrank', color:'#4CAF50', label:'Global OpenRank'},
        {key:'community_openrank', color:'#2196F3', label:'Community OpenRank'},
        {key:'avg_activity', color:'#FF9800', label:'Avg Activity'},
      ];

      const chartContainer = document.createElement('div');
      chartContainer.style.marginTop = '20px';

      // 添加图例
      const legendContainer = document.createElement('div');
      legendContainer.style.display = 'flex';
      legendContainer.style.flexWrap = 'wrap';
      legendContainer.style.marginBottom = '10px';

      metrics.forEach(m => {
        const legendItem = document.createElement('div');
        legendItem.style.display = 'flex';
        legendItem.style.alignItems = 'center';
        legendItem.style.marginRight = '15px';

        const colorBox = document.createElement('div');
        colorBox.style.width = '15px';
        colorBox.style.height = '15px';
        colorBox.style.backgroundColor = m.color;
        colorBox.style.marginRight = '5px';

        const labelSpan = document.createElement('span');
        labelSpan.innerText = m.label;

        legendItem.appendChild(colorBox);
        legendItem.appendChild(labelSpan);
        legendContainer.appendChild(legendItem);
      });
      chartContainer.appendChild(legendContainer);

      // 找出最大总和，用于缩放条长
      let maxTotal = 0;
      const devDataMap = {};
      recommendation.assignee.forEach(assignee => {
        const devData = statsData.find(d => d.developer === assignee) || {};
        const total = metrics.reduce((sum,m) => sum + (devData[m.key] || 0), 0);
        if (total > maxTotal) maxTotal = total;
        devDataMap[assignee] = {devData, total};
      });

      // 最大总和对应300px宽度
      const baseWidth = 300;

      recommendation.assignee.forEach(assignee => {
        const {devData, total} = devDataMap[assignee];
        const barContainer = document.createElement('div');
        barContainer.style.display = 'flex';
        barContainer.style.alignItems = 'center';
        barContainer.style.marginBottom = '8px';

        const nameSpan = document.createElement('span');
        nameSpan.innerText = assignee + ': ';
        nameSpan.style.width = '100px';
        barContainer.appendChild(nameSpan);

        const scale = maxTotal > 0 ? (total / maxTotal) : 0;
        const barWidth = scale * baseWidth;

        const barWrapper = document.createElement('div');
        barWrapper.style.display = 'flex';
        barWrapper.style.width = barWidth + 'px';
        barWrapper.style.height = '25px';
        barWrapper.style.background = '#eee';
        barWrapper.style.position = 'relative';
        barWrapper.style.marginRight = '10px';
        barWrapper.style.borderRadius = '4px';
        barWrapper.style.overflow = 'hidden';

        let currentLeft = 0;

        metrics.forEach(m => {
          const val = devData[m.key] || 0;
          if (val <= 0 || total === 0) {
            return;
          }
          const fraction = val/total;
          const segWidth = fraction * barWidth;

          const seg = document.createElement('div');
          seg.style.width = segWidth+'px';
          seg.style.background = m.color;
          seg.style.position = 'relative';
          seg.style.display = 'flex';
          seg.style.alignItems = 'center';
          seg.style.justifyContent = 'center';
          seg.style.color = '#fff';
          seg.style.fontSize = '12px';
          seg.style.fontWeight = 'bold';
          seg.style.boxSizing = 'border-box';

          seg.innerText = val.toFixed(2); // 显示值

          barWrapper.appendChild(seg);
          currentLeft += segWidth;
        });

        barContainer.appendChild(barWrapper);
        chartContainer.appendChild(barContainer);
      });

      displayArea.appendChild(chartContainer);
    })
    .catch(err => {
      console.error('Error fetching developer stats:', err);
    });
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    addResolverButton();
  } else {
    document.addEventListener('DOMContentLoaded', addResolverButton);
  }

})();

(function() {
  console.log('Content script loaded');

  // 检查是否为Issue页面
  const isIssuePage = () => {
    return /^\/[^\/]+\/[^\/]+\/issues\/\d+$/.test(window.location.pathname);
  };

  console.log('Current pathname:', window.location.pathname);
  console.log('Is issue page:', isIssuePage());

  // 获取用户登录名
  function getUserLogin() {
    const meta = document.querySelector('meta[name="user-login"]');
    if (meta) {
      return meta.getAttribute('content');
    } else {
      return null;
    }
  }

  function addResolverButton() {
    // 首先检查当前页面是否issue页面
    if (!isIssuePage()) {
      console.log('Not an issue page');
      return;
    }

    console.log('Adding resolver button');

    // 避免重复添加
    if (document.getElementById('issue-resolver-button')) return;

    const button = document.createElement('button');
    button.id = 'issue-resolver-button';
    button.innerText = 'View possible resolvers for this issue';
    button.style.marginLeft = '10px';
    button.style.position = 'relative';
    button.style.zIndex = '1000'; 
    button.classList.add('btn', 'btn-sm');

    const actionsBar = document.querySelector('.gh-header-actions');
    if (actionsBar) {
      console.log('Found actions bar');
      actionsBar.appendChild(button);
    } else {
      console.log('Actions bar not found, trying header');
      const header = document.querySelector('.gh-header-show');
      if (header) {
        header.appendChild(button);
      } else {
        console.log('Header not found');
        return;
      }
    }

    button.addEventListener('click', () => {
      console.log('Button clicked');
      const pathParts = location.pathname.split('/');
      const owner = pathParts[1];
      const repo = pathParts[2];
      const issueNumber = pathParts[4];

      console.log('Owner:', owner, 'Repo:', repo, 'Issue Number:', issueNumber);

      const requestData = {
        owner: owner,
        name: repo,
        number: parseInt(issueNumber)
      };

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
        if (data && data.recommendations && data.recommendations.length > 0) {
          showResolvers(data.recommendations, owner, repo, issueNumber);
        } else {
          alert('No possible resolvers found.');
        }
      })
      .catch(error => {
        console.error('Error fetching issue resolvers:', error);
        alert('Error fetching possible resolvers.');
      });
    });
  }

  function showResolvers(recommendations, owner, repo, issueNumber) {
    console.log('Showing resolvers');
    let container = document.getElementById('issue-resolver-container');
    if (container) {
      container.remove();
    }

    container = document.createElement('div');
    container.id = 'issue-resolver-container';
    container.style.marginTop = '20px';

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

    const displayArea = document.createElement('div');
    container.appendChild(displayArea);

    modelSelector.addEventListener('change', () => {
      const selectedIndex = modelSelector.value;
      displayRecommendation(recommendations[selectedIndex], owner, repo, issueNumber);
    });

    // 默认显示第一个模型的结果
    displayRecommendation(recommendations[0], owner, repo, issueNumber);

    const discussionTimeline = document.querySelector('.js-discussion');
    if (discussionTimeline) {
      discussionTimeline.parentNode.insertBefore(container, discussionTimeline);
    } else {
      const header = document.querySelector('.gh-header');
      if (header) {
        header.parentNode.insertBefore(container, header.nextSibling);
      }
    }
  }

  function displayRecommendation(recommendation, owner, repo, issueNumber) {
    const displayArea = document.querySelector('#issue-resolver-container > div');
    if (!displayArea) return;

    displayArea.innerHTML = '';

    const container = document.createElement('div');
    container.style.display = 'flex';
    container.style.alignItems = 'center';
    container.style.justifyContent = 'center';

    const resolverContainer = document.createElement('div');

    const title = document.createElement('h3');
    title.innerText = `Model: ${recommendation.model}`;
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
      probSpan.innerText = `(Probability:${(probability * 100).toFixed(4)}%)`;
      probSpan.style.marginLeft = '10px';
      probSpan.style.color = '#888';

      item.appendChild(link);
      item.appendChild(probSpan);
      list.appendChild(item);
    });

    container.appendChild(resolverContainer);

    // Feedback Container
    const feedbackContainer = document.createElement('div');
    feedbackContainer.style.marginLeft = '20px';
    feedbackContainer.style.display = 'flex';
    feedbackContainer.style.flexDirection = 'column';
    feedbackContainer.style.alignItems = 'center';

    const feedbackTitle = document.createElement('h3');
    feedbackTitle.innerText = 'Was this result helpful to you?';
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

    container.appendChild(feedbackContainer);

    displayArea.appendChild(container);

    let feedbackGiven = false;
    thumbsUp.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsUp.style.color = 'green';
      thumbsDown.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    thumbsDown.addEventListener('click', () => {
      if (feedbackGiven) return;
      feedbackGiven = true;

      thumbsDown.style.color = 'red';
      thumbsUp.style.color = '';

      const userLogin = getUserLogin();
      if (!userLogin) {
        alert('Unable to retrieve your username, please ensure you are logged in.');
        return;
      }

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
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        alert('Thank you for your feedback!');
      })
      .catch(error => {
        console.error('Error submitting feedback:', error);
        alert('Error submitting feedback.');
      });
    });

    // 获取开发者的统计数据并展示为堆叠条形图（仅global_openrank、community_openrank、avg_activity）
    fetch('http://localhost:8000/get_developer_stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        owner: owner,
        name: repo,
        developers: recommendation.assignee
      })
    })
    .then(res => {
      if (!res.ok) throw new Error('Failed to fetch developer stats');
      return res.json();
    })
    .then(statsData => {
      const metrics = [
        {key:'global_openrank', color:'#4CAF50', label:'Global OpenRank'},
        {key:'community_openrank', color:'#2196F3', label:'Community OpenRank'},
        {key:'avg_activity', color:'#FF9800', label:'Avg Activity'},
      ];

      const chartContainer = document.createElement('div');
      chartContainer.style.marginTop = '20px';

      // 添加图例
      const legendContainer = document.createElement('div');
      legendContainer.style.display = 'flex';
      legendContainer.style.flexWrap = 'wrap';
      legendContainer.style.marginBottom = '10px';

      metrics.forEach(m => {
        const legendItem = document.createElement('div');
        legendItem.style.display = 'flex';
        legendItem.style.alignItems = 'center';
        legendItem.style.marginRight = '15px';

        const colorBox = document.createElement('div');
        colorBox.style.width = '15px';
        colorBox.style.height = '15px';
        colorBox.style.backgroundColor = m.color;
        colorBox.style.marginRight = '5px';

        const labelSpan = document.createElement('span');
        labelSpan.innerText = m.label;

        legendItem.appendChild(colorBox);
        legendItem.appendChild(labelSpan);
        legendContainer.appendChild(legendItem);
      });
      chartContainer.appendChild(legendContainer);

      // 找出最大总和，用于缩放条长
      let maxTotal = 0;
      const devDataMap = {};
      recommendation.assignee.forEach(assignee => {
        const devData = statsData.find(d => d.developer === assignee) || {};
        const total = metrics.reduce((sum,m) => sum + (devData[m.key] || 0), 0);
        if (total > maxTotal) maxTotal = total;
        devDataMap[assignee] = {devData, total};
      });

      // 最大总和对应300px宽度
      const baseWidth = 300;

      recommendation.assignee.forEach(assignee => {
        const {devData, total} = devDataMap[assignee];
        const barContainer = document.createElement('div');
        barContainer.style.display = 'flex';
        barContainer.style.alignItems = 'center';
        barContainer.style.marginBottom = '8px';

        const nameSpan = document.createElement('span');
        nameSpan.innerText = assignee + ': ';
        nameSpan.style.width = '100px';
        barContainer.appendChild(nameSpan);

        const scale = maxTotal > 0 ? (total / maxTotal) : 0;
        const barWidth = scale * baseWidth;

        const barWrapper = document.createElement('div');
        barWrapper.style.display = 'flex';
        barWrapper.style.width = barWidth + 'px';
        barWrapper.style.height = '25px';
        barWrapper.style.background = '#eee';
        barWrapper.style.position = 'relative';
        barWrapper.style.marginRight = '10px';
        barWrapper.style.borderRadius = '4px';
        barWrapper.style.overflow = 'hidden';

        let currentLeft = 0;

        metrics.forEach(m => {
          const val = devData[m.key] || 0;
          if (val <= 0 || total === 0) {
            return;
          }
          const fraction = val/total;
          const segWidth = fraction * barWidth;

          const seg = document.createElement('div');
          seg.style.width = segWidth+'px';
          seg.style.background = m.color;
          seg.style.position = 'relative';
          seg.style.display = 'flex';
          seg.style.alignItems = 'center';
          seg.style.justifyContent = 'center';
          seg.style.color = '#fff';
          seg.style.fontSize = '12px';
          seg.style.fontWeight = 'bold';
          seg.style.boxSizing = 'border-box';

          // 如果段宽度太小，不显示文字，只显示颜色，鼠标悬停显示
          if (segWidth < 30) {
            seg.innerText = '';
          } else {
            seg.innerText = val.toFixed(2); 
          }

          // 鼠标悬停提示
          seg.title = `${m.label}: ${val.toFixed(2)}`;

          barWrapper.appendChild(seg);
          currentLeft += segWidth;
        });

        barContainer.appendChild(barWrapper);
        chartContainer.appendChild(barContainer);
      });

      displayArea.appendChild(chartContainer);
    })
    .catch(err => {
      console.error('Error fetching developer stats:', err);
    });
  }

  // 在初次加载页面以及GitHub使用PJAX导航（pjax:end事件）时运行addResolverButton
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    addResolverButton();
  } else {
    document.addEventListener('DOMContentLoaded', addResolverButton);
  }

  // 当GitHub使用PJAX加载新页面（包括切换到issue页面）时会触发pjax:end事件
  document.addEventListener('pjax:end', () => {
    addResolverButton();
  });
})();