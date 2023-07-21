$(document).ready(function() {

    // Initialize dropdowns
    $('#drop-down-1').dropdown();
    $('#drop-down-2').dropdown();
    var $dropdown1 = $('#drop-down-1 .menu');
    var $dropdown2 = $('#drop-down-2 .menu');


    // Initialize the slider 1
    $('#slider-1').slider({
        min: 20,
        max: 100,
        start: 30,
        step: 5,
        onChange: function(value) {
          console.log("Value of slider 1: " + value);  // Log the value when slider value changes
        }
    });
    // Initialize the slider 2
    $('#slider-2').slider({
        min: 20,
        max: 100,
        start: 30,
        step: 5,
        onChange: function(value) {
          console.log("Value of slider 2: " + value);  // Log the value when slider value changes
        }
    });


//var baseUrl =  "https://msi-app-b9364c344d37.herokuapp.com" // Jacob's Heroku
var baseUrl = "https://msi-webapp-7ba91279a938.herokuapp.com" //Sam's Heroku
//var baseUrl =  "http://127.0.0.1:8000"
// var baseUrl =  "http://localhost:8080"

    // Dropdown 1
      $.getJSON(baseUrl + '/diseases', function(diseases) {
      
        // Log that fetching diseases has being triggered
        console.log('Fetching diseases has being triggered');

        // Loop through each state in the returned data
        $.each(diseases, function(i, disease) {
            // Append a new dropdown item for each state
            $dropdown1.append('<div class="item" data-value="' + disease.value + '">' + disease.name + '</div>');
        });

        // Log that all diseases have been appended 
        console.log('All diseases have been appended ');

        // Initialize the dropdown
        $('#drop-down-1').dropdown();

        // Log that dropdown 1 initialised
        console.log('dropdown 1 initialised');
    });

    // Button 2, Find Drug Candidates
    // Updates the Dropdown 2 list
    // Event handlers for buttons
    $('#btn-2').click(function() {
        
        // Log that onChange is being triggered
        console.log('Find Drug Candidates Button triggered');

        var disease_label = $('#drop-down-1').dropdown('get value');

        // Log the name chosen disease from the Dropdown 1
        console.log("Chosen Disease label: " + disease_label);

        // Here you can send the disease_name, drug_name, k1 and k2 to your server and get the response
        // Example:
        $.ajax({
            url: baseUrl + '/drugs_for_disease',
            type: 'POST',
            data: JSON.stringify({ 
                disease_label: disease_label
            }),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(data) {
                var drug_candidates = data.drug_candidates;
                var console_logging_status = data.console_logging_status;
                
                // Show api response for debugging purposes
                console.log(console_logging_status);

                // Clear any existing items in the dropdown
                $dropdown2.empty();
                // Loop through each state in the returned data
                $.each(drug_candidates, function(i, drug) {
                    // Append a new dropdown item for each state
                    $dropdown2.append('<div class="item" data-value="' + drug.value + '">' + drug.name + '</div>');
                });

                // Initialize the dropdown
                $('#drop-down-2').dropdown();
            },

            
            error: function (request, status, error) {
                console.error('Error occurred:', error);
            }

        });
    });

    // Dropdown 2
    // Determining contents of Dropdown 2 is triggered by changes to dropdown 1
    // You need to extract the selected disease value and pass it in the POST request

    $('#dropdown-1').dropdown({
        onChange: function(value, text, $selectedItem) {

            // Log that onChange is being triggered
            console.log('onChange triggered');

            // Log the name when dropdown is selected
            console.log("Value of dropdown 1: " + JSON.stringify(value));

            // The value will contain the selected disease value
            // Send a post request for 
            $.ajax({
                url: baseUrl + '/diseases',
                type: 'POST',
                data: JSON.stringify({ name: value }), 
                contentType: "application/json; charset=utf-8",
                dataType: 'json',
                success: function(drug_candidates) {
                    // Clear any existing items in the dropdown
                    $dropdown2.empty();
                    // Loop through each state in the returned data
                    $.each(drug_candidates, function(i, drug) {
                        // Append a new dropdown item for each state
                        $dropdown2.append('<div class="item" data-value="' + drug.value + '">' + drug.name + '</div>');
                    });

                    // Initialize the dropdown
                    $('#dropdown-2').dropdown();
                },
                error: function (request, status, error) {
                    console.error('Error occurred:', error);
                }
            });
        }
    });


    // Event handlers for buttons
    $('#btn-1').click(function() {
        
        // Log that onChange is being triggered
        console.log('Generate Button triggered');

        var disease_label = $('#drop-down-1').dropdown('get value');
        var drug_label = $('#drop-down-2').dropdown('get value');
        var k1 = $('#slider-1').slider('get value');
        var k2 = $('#slider-2').slider('get value');

        // Log the name when dropdown is selected
        console.log("Chosen Disease label: " + disease_label);
        console.log("Chosen Drug label: " + drug_label);
        console.log("Slider 1 value: " + k1);
        console.log("Slider 2 value: " + k2);

        // Here you can send the disease_name, drug_name, k1 and k2 to your server and get the response
        // Example:
        $.ajax({
            url: baseUrl + '/graph',
            type: 'POST',
            data: JSON.stringify({ 
                disease_label: disease_label,
                drug_label: drug_label,
                k1: k1,
                k2: k2
            }),
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Handle the response from your server
                console.log("Graph Response: ", JSON.stringify(response));

                graphData = response.MOA_network;
                

                // Use vis-network to render the graphs
                new vis.Network(MOA_network, graphData, {});
            },
            error: function (request, status, error) {
                console.error('Error occurred:', error);
            }

        });
    });
});

window.addEventListener('DOMContentLoaded', (event) => {
    // Get the elements with the 'fade-in' and 'fade-in-no-delay' class
    const fadeInElements = document.querySelectorAll('.fade-in');
    const fadeInNoDelayElements = document.querySelectorAll('.fade-in-no-delay');
    // Add the 'visible' class to the elements
    fadeInElements.forEach(function (element) {
        element.classList.add('visible');
    });
    fadeInNoDelayElements.forEach(function (element) {
        element.classList.add('visible');
    });
});

document.addEventListener("DOMContentLoaded", function(){
    tippy('#btn-2', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Click to rank potential drug candidates based on their estimated impact on the selected disease.",
    });
    tippy('#Menu-1', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Select a disease that you're interested in exploring potential treatments for.",
    });
    tippy('#Menu-2', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Choose a drug to investigate its potential interactions with the selected disease.",
    });
    tippy('#Help-Button', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Need Help? Click for User Guide",
    });
    tippy('#btn-1', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Click this button to produce a visual map of the potential interactions between the chosen disease and drug.",
    });
    tippy('#Slider-1', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "Use this slider to adjust the range of the disease's impact on the body.",
    });
        tippy('#Slider-2', {
      theme: 'custom',
      arrow: false,
      animation: 'fade',
      content: "This slider allows you to control the projected reach of the drug in the body.",
    });
});

particlesJS('particles-js',
  // Paste your entire JSON data here.
	{
  "particles": {
    "number": {
      "value": 139,
      "density": {
        "enable": true,
        "value_area": 600
      }
    },
    "color": {
      "value": "#dd614a"
    },
    "shape": {
      "type": "circle",
      "stroke": {
        "width": 0,
        "color": "#000000"
      },
      "polygon": {
        "nb_sides": 3
      },
      "image": {
        "src": "..static/github.svg",
        "width": 100,
        "height": 100
      }
    },
    "opacity": {
      "value": 0.5,
      "random": true,
      "anim": {
        "enable": false,
        "speed": 1,
        "opacity_min": 0.1,
        "sync": false
      }
    },
    "size": {
      "value": 2,
      "random": true,
      "anim": {
        "enable": false,
        "speed": 19.446267532025583,
        "size_min": 1,
        "sync": false
      }
    },
    "line_linked": {
      "enable": true,
      "distance": 150,
      "color": "#73a580",
      "opacity": 0.3,
      "width": 1
    },
    "move": {
      "enable": true,
      "speed": 6,
      "direction": "none",
      "random": false,
      "straight": false,
      "out_mode": "out",
      "bounce": false,
      "attract": {
        "enable": true,
        "rotateX": 600,
        "rotateY": 1200
      }
    }
  },
  "interactivity": {
    "detect_on": "canvas",
    "events": {
      "onhover": {
        "enable": true,
        "mode": "repulse"
      },
      "onclick": {
        "enable": true,
        "mode": "bubble"
      },
      "resize": true
    },
    "modes": {
      "grab": {
        "distance": 400,
        "line_linked": {
          "opacity": 1
        }
      },
      "bubble": {
        "distance": 303.84793018789975,
        "size": 2.5,
        "duration": 0.24307834415031981,
        "opacity": 1,
        "speed": 3
      },
      "repulse": {
        "distance": 129.64178354683722,
        "duration": 0.4
      },
      "push": {
        "particles_nb": 4
      },
      "remove": {
        "particles_nb": 2
      }
    }
  },
  "retina_detect": true
}
)

class TextScramble {
    constructor(el) {
      this.el = el
      this.chars = '!<>-_\\/[]{}—=+*^?#________'
      this.update = this.update.bind(this)
    }
    setText(newText) {
      const oldText = this.el.innerText
      const length = Math.max(oldText.length, newText.length)
      const promise = new Promise((resolve) => this.resolve = resolve)
      this.queue = []
      for (let i = 0; i < length; i++) {
        const from = oldText[i] || ''
        const to = newText[i] || ''
        const start = Math.floor(Math.random() * 40)
        const end = start + Math.floor(Math.random() * 40)
        this.queue.push({ from, to, start, end })
      }
      cancelAnimationFrame(this.frameRequest)
      this.frame = 0
      this.update()
      return promise
    }
    update() {
      let output = ''
      let complete = 0
      for (let i = 0, n = this.queue.length; i < n; i++) {
        let { from, to, start, end, char } = this.queue[i]
        if (this.frame >= end) {
          complete++
          output += to
        } else if (this.frame >= start) {
          if (!char || Math.random() < 0.28) {
            char = this.randomChar()
            this.queue[i].char = char
          }
          output += `<span class="dud">${char}</span>`
        } else {
          output += from
        }
      }
      this.el.innerHTML = output
      if (complete === this.queue.length) {
        this.resolve()
      } else {
        this.frameRequest = requestAnimationFrame(this.update)
        this.frame++
      }
    }
    randomChar() {
      return this.chars[Math.floor(Math.random() * this.chars.length)]
    }
  }
  //Here is where you can change the words
  const phrases = [
    'Exploring the Multiscale Interactome',
  ]
  const phrases2 = [
    'Visualize and explore the hidden connections between diseases and potential drug treatments.',
  ]
  const el = document.querySelector('.scramble-text')
  const el2 = document.querySelector('.scramble-text-delay')
  const fx = new TextScramble(el)
  const fx2 = new TextScramble(el2)
  let counter = 0
  const next = () => {
    if(counter < phrases.length){
      fx.setText(phrases[counter]).then(() => {
        setTimeout(next, 800)
      })
      counter++
    }
  }
  let counter2 = 0
  const next2 = () => {
    if(counter2 < phrases2.length){
      fx2.setText(phrases2[counter2]).then(() => {
        setTimeout(next2, 800)
      })
      counter2++
    }
  }
  next()
  setTimeout(next2, 1500) // 2 seconds delay before starting the second scramble