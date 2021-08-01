(function ($) {
  "use strict";
  //start
  //end
  // Preloader
  $(window).on('load', function () {
    if ($('#preloader').length) {
      $('#preloader').delay(100).fadeOut('slow', function () {
        $(this).remove();
      });
    }
  });

  // Back to top button
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $('.back-to-top').fadeIn('slow');
    } else {
      $('.back-to-top').fadeOut('slow');
    }
  });

  $('.back-to-top').click(function(){
    $('html, body').animate({scrollTop : 0},1500, 'easeInOutExpo');
    return false;
  });
  
	var nav = $('nav');
	var navHeight = nav.outerHeight();

	/*--/ ScrollReveal /Easy scroll animations for web and mobile browsers /--*/
	window.sr = ScrollReveal();
	sr.reveal('.foo', { duration: 1000, delay: 15 });

	/*--/ Carousel owl /--*/
	$('#carousel').owlCarousel({
		loop: true,
		margin: -1,
		items: 1,
		nav: true,
		navText: ['<i class="ion-ios-arrow-back" aria-hidden="true"></i>', '<i class="ion-ios-arrow-forward" aria-hidden="true"></i>'],
		autoplay: true,
		autoplayTimeout: 3000,
		autoplayHoverPause: true
	});

	/*--/ Animate Carousel /--*/
	$('.intro-carousel').on('translate.owl.carousel', function () {
		$('.intro-content .intro-title').removeClass('zoomIn animated').hide();
		$('.intro-content .intro-price').removeClass('fadeInUp animated').hide();
		$('.intro-content .intro-title-top, .intro-content .spacial').removeClass('fadeIn animated').hide();
	});

	$('.intro-carousel').on('translated.owl.carousel', function () {
		$('.intro-content .intro-title').addClass('zoomIn animated').show();
		$('.intro-content .intro-price').addClass('fadeInUp animated').show();
		$('.intro-content .intro-title-top, .intro-content .spacial').addClass('fadeIn animated').show();
	});

	/*--/ Navbar Collapse /--*/
	$('.navbar-toggle-box-collapse').on('click', function () {
		$('body').removeClass('box-collapse-closed').addClass('box-collapse-open');
	});
	$('.close-box-collapse, .click-closed').on('click', function () {
		$('body').removeClass('box-collapse-open').addClass('box-collapse-closed');
		$('.menu-list ul').slideUp(700);
	});

	/*--/ Navbar Menu Reduce /--*/
	$(window).trigger('scroll');
	$(window).bind('scroll', function () {
		var pixels = 50;
		var top = 1200;
		if ($(window).scrollTop() > pixels) {
			$('.navbar-default').addClass('navbar-reduce');
			$('.navbar-default').removeClass('navbar-trans');
		} else {
			$('.navbar-default').addClass('navbar-trans');
			$('.navbar-default').removeClass('navbar-reduce');
		}
		if ($(window).scrollTop() > top) {
			$('.scrolltop-mf').fadeIn(1000, "easeInOutExpo");
		} else {
			$('.scrolltop-mf').fadeOut(1000, "easeInOutExpo");
		}
	});

	/*--/ Property owl /--*/
	$('#property-carousel').owlCarousel({
		loop: true,
		margin: 30,
		responsive: {
			0: {
				items: 1,
			},
			769: {
				items: 2,
			},
			992: {
				items: 3,
			}
		}
	});

	/*--/ Property owl owl /--*/
	$('#property-single-carousel').owlCarousel({
		loop: true,
		margin: 0,  
		nav: true,
		navText: ['<i class="ion-ios-arrow-back" aria-hidden="true"></i>', '<i class="ion-ios-arrow-forward" aria-hidden="true"></i>'],
		responsive: {
			0: {
				items: 1,
			}
		}
	});

	/*--/ News owl /--*/
	$('#new-carousel').owlCarousel({
		loop: true,
		margin: 30,
		responsive: {
			0: {  
				items: 1,
			},
			769: {
				items: 2,
			},
			992: {
				items: 3,
			}
		}
	});

	/*--/ Testimonials owl /--*/
	$('#testimonial-carousel').owlCarousel({
		margin: 0,
		autoplay: true,
		nav: true,
		animateOut: 'fadeOut',
		animateIn: 'fadeInUp',
		navText: ['<i class="ion-ios-arrow-back" aria-hidden="true"></i>', '<i class="ion-ios-arrow-forward" aria-hidden="true"></i>'],
		autoplayTimeout: 4000,
		autoplayHoverPause: true,
		responsive: {
			0: {
				items: 1,
			}
		}
	});

const updatePage = (context) => {
    //get the current page handle
//    var result = document.getElementsByClassName('nav-link');
//    $(".nav-link").each((index,value) => {
////        console.log(index,value);
////        $(this).removeClass("active");
//        console.log($(this).class());
//    });
}
updatePage()



// const picker =  handle => {
//     let start = new Date(),
//         prevDay,
//         startHours = 9;
//     // 09:00 AM
//     start.setHours(9);
//     start.setMinutes(0);
//     // If today is Saturday or Sunday set 10:00 AM
//     if ([6, 0].indexOf(start.getDay()) !== -1) {
//         start.setHours(10);
//         startHours = 10
//     }
//     $(`#${handle}`).datepicker({
//         language: 'en',
//         startDate: start,
//         autoClose: true,
//         view: "years",
//         maxDate: start,
//         dataView: "months",
//         position: "top left",
//         onSelect: function (fd, d, picker) {
//             // Do nothing if selection was cleared
//             if (!d) return;
//
//             var day = d.getDay();
//
//             // Trigger only if date is changed
//             if (prevDay !== undefined && prevDay === day) return;
//             prevDay = day;
//
//             // If chosen day is Saturday or Sunday when set
//             // hour value for weekends, else restore defaults
//             if (day === 6 || day === 0) {
//                 picker.update({
//                     minHours: 10,
//                     maxHours: 16
//                 })
//             } else {
//                 picker.update({
//                     minHours: 9,
//                     maxHours: 18
//                 })
//             }
//         }
//     });
// }
//
// picker("datePackerOne")

	function getJson(url,handleData){
    $.ajax({
        url: url,
        method: "POST",
        data: {
            category: "",
        },
        success: function (result) {
            handleData(result);
        }
    });
}
// let lnk = "68.183.89.127"
// // make a handle to the graph
// 	let doughnut_handle = $("#doughnut");
// 	let daily_chart = $("#myChart");
// 	// / here we are updating the doughnut
// 	getJson(`http://${lnk}:4000/graph/data/doughnut`,(data)=>{
// 		console.log("",data, data.serviced,data.unserviced)
// 		// new issues
// 		doughnut_handle.data.datasets[0].data[0] =  data.serviced;
// 		// closed issues
// 		doughnut_handle.data.datasets[0].data[1] =  data.unserviced;
// 		doughnut_handle.update();
// 	});
//
// 	// here we are updating the daily graph
// 	getJson(`http://${lnk}:4000/graph/data`,(data)=>{
//
// 		data.map((value,index)=>{
// 			myChart.data.datasets[0].data[index+1] =  value.issuesCount;
// 		});
// 		myChart.update();
// 	});et lnk = "68.183.89.127"
// // make a handle to the graph
// 	let doughnut_handle = $("#doughnut");
// 	let daily_chart = $("#myChart");
// 	// / here we are updating the doughnut
// 	getJson(`http://${lnk}:4000/graph/data/doughnut`,(data)=>{
// 		console.log("",data, data.serviced,data.unserviced)
// 		// new issues
// 		doughnut_handle.data.datasets[0].data[0] =  data.serviced;
// 		// closed issues
// 		doughnut_handle.data.datasets[0].data[1] =  data.unserviced;
// 		doughnut_handle.update();
// 	});
//
// 	// here we are updating the daily graph
// 	getJson(`http://${lnk}:4000/graph/data`,(data)=>{
//
// 		data.map((value,index)=>{
// 			myChart.data.datasets[0].data[index+1] =  value.issuesCount;
// 		});
// 		myChart.update();
// 	});et lnk = "68.183.89.127"
// // make a handle to the graph
// 	let doughnut_handle = $("#doughnut");
// 	let daily_chart = $("#myChart");
// 	// / here we are updating the doughnut
// 	getJson(`http://${lnk}:4000/graph/data/doughnut`,(data)=>{
// 		console.log("",data, data.serviced,data.unserviced)
// 		// new issues
// 		doughnut_handle.data.datasets[0].data[0] =  data.serviced;
// 		// closed issues
// 		doughnut_handle.data.datasets[0].data[1] =  data.unserviced;
// 		doughnut_handle.update();
// 	});
//
// 	// here we are updating the daily graph
// 	getJson(`http://${lnk}:4000/graph/data`,(data)=>{
//
// 		data.map((value,index)=>{
// 			myChart.data.datasets[0].data[index+1] =  value.issuesCount;
// 		});
// 		myChart.update();
// 	});

	   setTimeout(()=>{
        $('#branchOpens').clockpicker({
			placement: 'top',
			donetext : "Select Time"
		});
        $('#branchCloses').clockpicker({
			placement: 'top',
			donetext : "Select Time"
		});
    },2000)


})(jQuery);
