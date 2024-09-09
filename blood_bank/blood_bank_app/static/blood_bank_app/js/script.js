$(document).ready(function () {
    // Activate the carousel
    $('#carouselExampleIndicators').carousel({
        interval: 1000, // Change slide interval (in milliseconds)
        pause: 'hover' // Pause the carousel on hover
    });

    // Optional: Add custom code if needed
    // Example: Handle carousel events
    $('#carouselExampleIndicators').on('slide.bs.carousel', function (event) {
        console.log('Slide event: ', event);
    });
});

// Blood Availability dashboard statusbar

document.addEventListener("DOMContentLoaded", function () {
    const droplets = document.querySelectorAll('.droplet-container');

    droplets.forEach(droplet => {
        const daysRemaining = parseInt(droplet.querySelector('.days-remaining').textContent);

        if (daysRemaining < 8) {
            droplet.style.backgroundColor = rgb(216, 25, 19);
        } else {
            droplet.style.backgroundColor = rgb(122, 119, 119);
        }
    });
})





function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].style.backgroundColor = "";
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.style.backgroundColor = "#d81a13";
}
