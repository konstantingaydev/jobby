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
  ev.currentTarget.classList.add('kanban-drop-hover');
}

function dragLeaveHandler(ev) {
  ev.currentTarget.classList.remove('kanban-drop-hover');
}


function dropHandler(ev) {
  ev.preventDefault();
  const stageEl = ev.currentTarget;
  stageEl.classList.remove('kanban-drop-hover');
  const stageId = parseInt(stageEl.dataset.stageId, 10);
  const cardId = parseInt(ev.dataTransfer.getData('text/plain'), 10);




// Kanban drag-and-drop logic
let draggedCard = null;

function handleDragStart(e) {
  draggedCard = e.target;
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/plain', draggedCard.dataset.cardId);
  setTimeout(() => draggedCard.classList.add('dragging'), 0);
}

function handleDragEnd(e) {
  if (draggedCard) {
    draggedCard.classList.remove('dragging');
    draggedCard = null;
  }
}

function handleDragOver(e) {
  e.preventDefault();
  e.currentTarget.classList.add('kanban-drop-hover');
}

function handleDragLeave(e) {
  e.currentTarget.classList.remove('kanban-drop-hover');
}

function handleDrop(e) {
  e.preventDefault();
  e.currentTarget.classList.remove('kanban-drop-hover');
  if (!draggedCard) return;
  e.currentTarget.appendChild(draggedCard);
  draggedCard.classList.remove('dragging');
  draggedCard = null;
  // TODO: Add backend update logic here if needed
}

function initializeKanban() {
  document.querySelectorAll('.kanban-card').forEach(card => {
    card.setAttribute('draggable', 'true');
    card.removeEventListener('dragstart', handleDragStart);
    card.removeEventListener('dragend', handleDragEnd);
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragend', handleDragEnd);
  });
  document.querySelectorAll('.kanban-column').forEach(col => {
    col.removeEventListener('dragover', handleDragOver);
    col.removeEventListener('dragleave', handleDragLeave);
    col.removeEventListener('drop', handleDrop);
    col.addEventListener('dragover', handleDragOver);
    col.addEventListener('dragleave', handleDragLeave);
    col.addEventListener('drop', handleDrop);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeKanban);
} else {
  initializeKanban();
}
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
    column.addEventListener('dragleave', dragLeaveHandler);
    column.addEventListener('drop', dropHandler);
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeKanban);
} else {
  initializeKanban();
}
