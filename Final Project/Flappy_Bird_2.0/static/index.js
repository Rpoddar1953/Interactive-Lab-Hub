var request = new XMLHttpRequest();
request.open('POST', '/new_game');

request.onload = function() {
  if (request.status === 200 && request.responseText === 'done') {
    // long process finished successfully, redirect user
    window.location = '/mode';
  } else {
    // ops, we got an error from the server
    alert('Something went wrong.');
  }
};

request.onerror = function() {
  // ops, we got an error trying to talk to the server
  alert('Something went wrong.');
};

request.send();
