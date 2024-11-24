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


