$(document).ready(function() {
		$("#waking-slider-range").slider({
			range: true,
			min: 0,
			max: 1920,
			step: 5,
			values: [540, 1020],
			slide: function (e, ui) {
				var hours1 = String(Math.floor(ui.values[0] / 60));
				var minutes1 = String(ui.values[0] - (hours1 * 60));
				if (ui.values[0] >= 1440){
					hours1 = "23";
					minutes1 = "59";	
				}

				if (hours1.length == 1) hours1 = '0' + hours1;
				if (minutes1.length == 1) minutes1 = '0' + minutes1;
				if (minutes1 == 0) minutes1 = '00';

				$('#wake_up_time').val(hours1 + ':' + minutes1);

				var hours2 = String(Math.floor(ui.values[1] / 60));
				var minutes2 = String(ui.values[1] - (hours2 * 60));
				if (ui.values[1] >= 1440){
					hours2 = String(parseInt(hours2) - 24);					
				}

				if (hours2.length == 1) hours2 = '0' + hours2;
				if (minutes2.length == 1) minutes2 = '0' + minutes2;
				if (minutes2 == 0) minutes2 = '00';

				$('#bed_time').val(hours2 + ':' + minutes2);
					//calculate the duration in hours/minutes.
				var duration1 = ui.values[1] - ui.values[0];
				var duration_hours = Math.floor(duration1 / 60);
				var duration_minutes = Math.floor(duration1 - (duration_hours * 60));
				var hours_text = "hours";
				var minutes_text = "minutes";
				
				if (duration_hours == 1){
					hours_text = "hour";
					}
				if (duration_minutes == 1){
					minutes_text = "minute";
					}
					
				$('.slider-duration').html(duration_hours + " " + hours_text + " and " + duration_minutes + " " + minutes_text + ". (" + hours1 + ':' + minutes1 + " to " + hours2 + ':' + minutes2 + ")");
				
			}
		});
				//initialise the slider if there are values already loaded into the start and end times
				var start_time_total_minutes = 0;
				var end_time_total_minutes = 0;
				
				if ($('#wake_up_time').val()){
					var start_time = $('#wake_up_time').val();
					//parse and convert to a number of minutes (0-1440)
					var start_time_hours = start_time.substring(0, start_time.indexOf(":"));
					start_time = start_time.substring(start_time.indexOf(":")+1);
					var start_time_minutes = start_time.substring(0, start_time.indexOf(":"));
					start_time_total_minutes = (parseInt(start_time_hours)*60) + parseInt(start_time_minutes);
					//alert("start_time_hours: " + start_time_hours + "\nstart_time_minutes: " + start_time_minutes + "\ntotal_minutes: " + start_time_total_minutes);
				}
				if ($('#bed_time').val()){
					var end_time = $('#bed_time').val();
					//parse and convert to a number of minutes (0-1440)
					var end_time_hours = end_time.substring(0, end_time.indexOf(":"));
					end_time = end_time.substring(end_time.indexOf(":")+1);
					var end_time_minutes = end_time.substring(0, end_time.indexOf(":"));
					end_time_total_minutes = (parseInt(end_time_hours)*60) + parseInt(end_time_minutes);
					//alert("end_time_hours: " + end_time_hours + "\n end_time_minutes: " + end_time_minutes + "\n end_time_total_minutes: " + end_time_total_minutes);
				}
				
				$( "#waking-slider-range" ).slider('values',0,start_time_total_minutes);
				$( "#waking-slider-range" ).slider('values',1,end_time_total_minutes);
				
			});