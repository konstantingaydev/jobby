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
  draggedCard = ev.target;
  ev.dataTransfer.setData('text/plain', ev.target.dataset.cardId);
  ev.dataTransfer.effectAllowed = 'move';
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

  // Compute position (end of column)
  const toOrder = stageEl.querySelectorAll('.kanban-card').length + 1;

  // Optimistically move in DOM
  if (draggedCard) {
    stageEl.appendChild(draggedCard);
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
    console.error(err);
    alert('Network error while moving card');
    window.location.reload();
  });
}
