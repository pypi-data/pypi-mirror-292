// File     : check_closing
// Source   : https://community.plotly.com/t/automatic-server-shutdown-upon-browser-tab-closure/79538
// Purpose  : Send a shutdown signal to the python network editor when tab is closed

// Open dialogue window before leaving the page
// window.addEventListener('beforeunload', function (e) {
//     e.preventDefault();
// });

// // Extra checker to send shutdown signal
// window.addEventListener("onbeforeunload", function (e) {
//     fetch('/shutdown', { method: 'POST' });
// });

// // Shutdown the server if the usere exits
// window.addEventListener("unload", function (e) {
//     fetch('/shutdown', { method: 'POST' });
// });