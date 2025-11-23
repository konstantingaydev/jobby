function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

let draggedCard = null;

function dragStartHandler(ev) {
  draggedCard = ev.target.closest('.kanban-card');
  if (!draggedCard) return;
  
  ev.dataTransfer.setData('text/plain', draggedCard.dataset.cardId);
  ev.dataTransfer.effectAllowed = 'move';
  draggedCard.style.opacity = '0.5';
}

function dragEndHandler(ev) {
  if (draggedCard) {
    draggedCard.style.opacity = '1';
  }
}

function dragOverHandler(ev) {
  ev.preventDefault();
  ev.dataTransfer.dropEffect = 'move';
}

function dropHandler(ev) {
  ev.preventDefault();
  const stageEl = ev.currentTarget;
  const stageId = parseInt(stageEl.dataset.stageId, 10);
  const cardId = parseInt(ev.dataTransfer.getData('text/plain'), 10);

  if (!cardId || !stageId) {
    console.error('Invalid card or stage ID');
    return;
  }

  // Compute position (end of column)
  const toOrder = stageEl.querySelectorAll('.kanban-card').length + 1;

  // Optimistically move in DOM
  if (draggedCard) {
    stageEl.appendChild(draggedCard);
    draggedCard.style.opacity = '1';
  }

  // Call backend
  const csrftoken = getCookie('csrftoken');
  fetch('/recruiter/kanban/move_card/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({ card_id: cardId, to_stage: stageId, to_order: toOrder })
  }).then(r => r.json()).then(data => {
    if (!data.ok) {
      alert('Error moving card: ' + (data.error || 'unknown'));
      window.location.reload();
    }
  }).catch(err => {
    console.error('Network error:', err);
    alert('Network error while moving card');
    window.location.reload();
  });
}

// Initialize drag and drop event listeners
function initializeKanban() {
  // Add event listeners to all kanban cards
  document.querySelectorAll('.kanban-card').forEach(card => {
    card.addEventListener('dragstart', dragStartHandler);
    card.addEventListener('dragend', dragEndHandler);
  });

  // Add event listeners to all kanban columns
  document.querySelectorAll('.kanban-column').forEach(column => {
    column.addEventListener('dragover', dragOverHandler);
    column.addEventListener('drop', dropHandler);
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeKanban);
} else {
  initializeKanban();
}
