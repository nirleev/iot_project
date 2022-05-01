var socket = io();
socket.on('connect', function() {
  console.log('connect');

  socket.on('newdata', function(data) {
    const t = document.querySelector('#main');
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.innerText = data.value;
    row.appendChild(cell);
    t.appendChild(row);
  });

  socket.on('disconnect', function() {
    console.log('bye');
  })
});