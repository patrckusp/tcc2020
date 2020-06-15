$(document).ready(function () {
	String.prototype.splice = function(idx, rem, str) {
		return this.slice(0, idx) + str + this.slice(idx + Math.abs(rem));
	};
});

$('#new-classifier').submit(function(e) {
	e.preventDefault();
	data = $(this).serialize();
		
	emptyResults = '<div id="news-text-tip"><div><canvas id="chartContainer"></canvas>';
	
	if(myPieChart != null) 
		myPieChart.destroy();

	$.getJSON('get_news_categories.php', data, function(response) {
		showResults = $('#show-results');
		if(showResults.hasClass('d-none')) {
			showResults.removeClass('d-none');
		}
		
		colors = ['#007bff', '#6610f2', '#6f42c1', '#e83e8c', '#dc3545', '#fd7e14', '#ffc107', '#28a745', '#20c997', '#17a2b8','#6c757d', '#beb351', '#ed16a5']
		
		dataAux = [];
		labelsAux = [];
		colorsAux = [];
		count = 0;
		$.each(response['classification'], function(key, value) {
			if(value.toFixed(2) > 0) {
				dataAux.push(parseFloat((value*100).toFixed(2)));
				labelsAux.push(key);
				colorsAux.push(colors[count++]);
			}
		});
		
		chartData = {
			datasets: [{
				data: dataAux,
				backgroundColor: colorsAux,
				borderWidth: 1
			}],
			
			// These labels appear in the legend and in the tooltips when hovering different arcs
			labels: labelsAux
		};

		var ctx = document.getElementById('chartContainer').getContext('2d');
		myPieChart = new Chart(ctx, {
			type: 'pie',
			data: chartData,
			options: {
				responsive: true,
				legend: {
					position: 'top',
				},
				title: {
					display: false,
					text: 'Chart.js Doughnut Chart'
				},
				animation: {
					animateScale: true,
					animateRotate: true
				},
				plugins: {
					labels: {
						render: 'percentage',
						fontColor: 'black',
						position: 'border',
						precision: 2
					}
				},
				tooltips: {
					callbacks: {
						label: function(tooltipItem, data) {
							var dataset = data.datasets[tooltipItem.datasetIndex];
							var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
								return previousValue + currentValue;
							});
							var currentValue = dataset.data[tooltipItem.index];
							var percentage = currentValue/total * 100;         
							return data.labels[tooltipItem.index] + ': ' + percentage + "%";
						}
					}
				}
			}
		});

		text = $('#news-text').val();
		$.each(response['ner'], function(key, value) {
			entityPosition = text.indexOf(value[0]);
			
			text = text.splice(entityPosition + value[0].length, 0, `</button>`);
			text = text.splice(entityPosition, 0, `<button data-tippy-content="${value[1]}">`);
		});
		$('#news-text-tip').html(text);
		tippy('[data-tippy-content]');
		tippy('button', {
			duration: 0,
			arrow: true,
			delay: [1000, 200],
		  });
		
	});
});