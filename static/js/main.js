var socket = io();
socket.on('connect', function() {
  console.log('connect');

  socket.on('newdata', function(data) {
    const t = document.querySelector('#main');
    const row = document.createElement('tr');
    const c_date = document.createElement('td');
    const c_temp = document.createElement('td');
    c_date.innerText = data.date;
    c_temp.innerText = data.temp;
    row.appendChild(c_date);
    row.appendChild(c_temp);
    t.appendChild(row);
  });

  socket.on('disconnect', function() {
    console.log('bye');
  })
});