document.addEventListener('DOMContentLoaded', function() {
	var pythonShell;
	var pythonProcess;
	var pyshell;
	var start = true;

	var e = document.getElementById("objects")
	var object = e.options[e.selectedIndex].text;
	e.addEventListener("change", function () {
		object = e.options[e.selectedIndex].text;
	});

	var b = document.getElementById("controlButton")
	var c = document.getElementById("connectedStatus")
	var t = document.getElementById("trackingStatus")
	var o = document.getElementById("objectPosition")

	b.addEventListener("click", function () {
		if (start == true)
		{
			pythonShell = require('python-shell');
			console.log(object)
			var arg = '--object=' + object
			var options = {
				mode: 'text',
				pythonOptions: ['-u'],
				args: [arg]
			};

			pyshell = new pythonShell('darknet_webcam.py', options)

			pyshell.on('message', function (message) {
				// received a message sent from the Python script (a simple "print" statement)
				if (message.trim() === "Connecting...")
				{
					c.style.background = '#ffa31a';
					c.textContent  = "Connecting..."
					t.style.background = '#ffa31a';
					t.textContent  = "Preparing tracker..."
				}
				else if (message.trim() === "Connected!"){
					c.style.background = '#4dff4d';
					c.textContent  = "Connected"
					t.style.background = '#4dff4d';
					t.textContent  = "Tracking"
				}
				else if (message.includes("(")){
					o.textContent  = message
				}
			});

			pyshell.end(function (err) {
		        if (err) {
		            console.log(err);
		        }
		    });

		    start = false;
		    b.style.background = "#f2190e";
		    b.value = "Stop"
		}
		else
		{
			pyshell.terminate('SIGINT');

			c.style.background = '#955';
			c.textContent  = "Not connected"
			t.style.background = '#955';
			t.textContent  = "Not tracking"

			start = true;
			b.style.background = "#3faa44";
		    b.value = "Start"

		    o.textContent  = "N/A"
		}
	});
})
