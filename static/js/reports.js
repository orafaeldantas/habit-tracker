

const habits = JSON.parse(document.getElementById('habits-data').textContent);

const ctx = document.getElementById('active-completed-habits');


  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Hábitos Pendentes', 'Hábitos Concluídos'],
      datasets: [{
        label: '',
        data: [habits['pending_habits'], habits['completed_habits']],
        borderWidth: 1
      }]
    },
    options: {
    }
  });

const rate = document.getElementById('rate');

  new Chart(rate, {
    type: 'bar',
    data:{
      labels: [''],
      datasets: [{
          label: 'Taxa de conclusão %',         
          data: [habits['completion_rate']]
      }]
    },
    options: {
      indexAxis: 'y',
      scales: {
        x: {
            suggestedMin: 0,
            suggestedMax: 100
        },

      }
    },    
  });


const weekday = document.getElementById('weekday');

  new Chart(weekday, {
  type: "line",
  data: {
    labels: ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-fera', 'Sexta-feira', 'Sábado'],
      datasets: [{
          label: 'Hábitos Concluídos por dia em %',         
          data: [habits['Sunday'],
                 habits['Monday'], 
                 habits['Tuesday'],
                 habits['Wednesday'], 
                 habits['Thursday'],
                 habits['Friday'],
                 habits['Saturday']]
      }]
  },
  options: {
    indexAxis: 'x',
      scales: {
        y: {
            suggestedMin: 0,
            suggestedMax: 100
        },

      }
  }
});