/*

=========================================================
* Rocket - Startup Bootstrap Template
=========================================================

* Product Page: https://themes.getbootstrap.com/product/rocket/
* Copyright 2020 Themesberg (https://www.themesberg.com)
* License (https://themes.getbootstrap.com/licenses/)

* Coded by https://themesberg.com

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

"use strict";
$(document).ready(function () {

    // preloader
    var $preloader = $('.preloader');
    if($preloader.length) {
        $preloader.delay(500).fadeOut('slow');
    }

    // options
    var breakpoints = {
        sm: 540,
        md: 720,
        lg: 960,
        xl: 1140
    };

    var $navbarCollapse = $('.navbar-main .collapse');

    // Collapse navigation
    $navbarCollapse.on('hide.bs.collapse', function () {
        var $this = $(this);
        $this.addClass('collapsing-out');
        $('html, body').css('overflow', 'initial');
    });

    $navbarCollapse.on('hidden.bs.collapse', function () {
        var $this = $(this);
        $this.removeClass('collapsing-out');
    });

    $navbarCollapse.on('shown.bs.collapse', function () {
        $('html, body').css('overflow', 'hidden');
    });

    $('.navbar-main .dropdown').on('hide.bs.dropdown', function () {
        var $this = $(this).find('.dropdown-menu');

        $this.addClass('close');

        setTimeout(function () {
            $this.removeClass('close');
        }, 200);

    });

    $('.dropdown-menu a.dropdown-toggle').on('click', function(e) {
        if (!$(this).next().hasClass('show')) {
          $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
        }
        var $subMenu = $(this).next(".dropdown-menu");
        $subMenu.toggleClass('show');
      
        $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
          $('.dropdown-submenu .show').removeClass("show");
        });
      
        return false;
    });

    if ($(document).width() >= breakpoints.lg) {
        $('.nav-item.dropdown').hover(function() {
            $(this).find('> .dropdown-toggle').dropdown('toggle');
        },
        function () {
            $(this).removeClass('show');
            $(this).find('.dropdown-menu').removeClass('show');
            $(this).find('> .dropdown-toggle').attr('aria-expanded', 'false');
        });
    
        $('.dropdown-menu a.dropdown-toggle').hover(function() {
            if (!$(this).next().hasClass('show')) {
                $(this).parents('.dropdown-menu').first().find('.show').removeClass("show");
              }
              var $subMenu = $(this).next(".dropdown-menu");
              $subMenu.toggleClass('show');
            
              $(this).parents('li.nav-item.dropdown.show').on('hidden.bs.dropdown', function(e) {
                $('.dropdown-submenu .show').removeClass("show");
              });
            
              return false;
        },
        function () {
            $(this).removeClass('show');
            $(this).find('.dropdown-menu').removeClass('show');
            $(this).attr('aria-expanded', false);
        });
    }

    // Headroom - show/hide navbar on scroll
    if ($('.headroom')[0]) {
        var headroom = new Headroom(document.querySelector("#navbar-main"), {
            offset: 0,
            tolerance: {
                up: 1,
                down: 0
            },
        });
        headroom.init();
    }

    // Background images for sections
    $('[data-background]').each(function () {
        $(this).css('background-image', 'url(' + $(this).attr('data-background') + ')');
    });

    $('[data-background-color]').each(function () {
        $(this).css('background-color', $(this).attr('data-background-color'));
    });

    $('[data-color]').each(function () {
        $(this).css('color', $(this).attr('data-color'));
    });

    // Datepicker
    $('.datepicker')[0] && $('.datepicker').each(function () {
        $('.datepicker').datepicker({
            disableTouchKeyboard: true,
            autoclose: false
        });
    });

    // Tooltip
    $('[data-toggle="tooltip"]').tooltip();

    // Popover
    $('[data-toggle="popover"]').each(function () {
        var popoverClass = '';
        if ($(this).data('color')) {
            popoverClass = 'popover-' + $(this).data('color');
        }
        $(this).popover({
            trigger: 'focus',
            template: '<div class="popover ' + popoverClass + '" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
        })
    });

    // Additional .focus class on form-groups
    $('.form-control').on('focus blur', function (e) {
        $(this).parents('.form-group').toggleClass('focused', (e.type === 'focus' || this.value.length > 0));
    }).trigger('blur');

    var e = document.querySelector('[data-toggle="price"]');
    "undefined" != typeof CountUp && e && e.addEventListener("change", function(e) {
        ! function(e) {
            var t = e.target,
                d = t.checked,
                a = t.dataset.target,
                o = document.querySelectorAll(a);
            [].forEach.call(o, function(e) {
                var t = e.dataset.annual,
                    a = e.dataset.monthly,
                    o = e.dataset.decimals ? e.dataset.decimals : null,
                    n = e.dataset.duration ? e.dataset.duration : 1,
                    r = e.dataset.options ? JSON.parse(e.dataset.options) : null,
                    l = d ? new CountUp(e, t, a, o, n, r) : new CountUp(e, a, t, o, n, r);
                l.error ? console.error(l.error) : l.start()
            })
        }(e)
    })


    // NoUI Slider
    if ($(".input-slider-container")[0]) {
        $('.input-slider-container').each(function () {

            var slider = $(this).find('.input-slider');
            var sliderId = slider.attr('id');
            var minValue = slider.data('range-value-min');
            var maxValue = slider.data('range-value-max');

            var sliderValue = $(this).find('.range-slider-value');
            var sliderValueId = sliderValue.attr('id');
            var startValue = sliderValue.data('range-value-low');

            var c = document.getElementById(sliderId),
                d = document.getElementById(sliderValueId);

            noUiSlider.create(c, {
                start: [parseInt(startValue)],
                connect: [true, false],
                //step: 1000,
                range: {
                    'min': [parseInt(minValue)],
                    'max': [parseInt(maxValue)]
                }
            });

            c.noUiSlider.on('update', function (a, b) {
                d.textContent = a[b];
            });
        })
    }

    // When in viewport
    $('[data-toggle="on-screen"]')[0] && $('[data-toggle="on-screen"]').onScreen({
        container: window,
        direction: 'vertical',
        doIn: function () {
            //alert();
        },
        doOut: function () {
            // Do something to the matched elements as they get off scren
        },
        tolerance: 200,
        throttle: 50,
        toggleClass: 'on-screen',
        debug: false
    });

    // Scroll to anchor with scroll animation
    $('[data-toggle="scroll"]').on('click', function (event) {
        var hash = $(this).attr('href');
        var offset = $(this).data('offset') ? $(this).data('offset') : 0;

        // Animate scroll to the selected section
        $('html, body').stop(true, true).animate({
            scrollTop: $(hash).offset().top - offset
        }, 600);

        event.preventDefault();
    });

    //Chartist

    if($('.ct-chart-ranking').length) {
        //Chart 5
            new Chartist.Bar('.ct-chart-ranking', {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            series: [
                [5, 4, 3, 7, 5, 10, 3],
                [3, 2, 9, 5, 4, 6, 4]
            ]
            }, {
            low: 0,
            showArea: true,
            plugins: [
                Chartist.plugins.tooltip()
            ],
            axisX: {
                // On the x-axis start means top and end means bottom
                position: 'end'
            },
            axisY: {
                // On the y-axis start means left and end means right
                showGrid: false,
                showLabel: false,
                offset: 0
            }
        });
    }

    if($('.ct-chart-traffic-source').length) {
        var data = {
            series: [80, 20, 10]
            };
            
            var sum = function(a, b) { return a + b };
            
            new Chartist.Pie('.ct-chart-traffic-source', data, {
            labelInterpolationFnc: function(value) {
                return Math.round(value / data.series.reduce(sum) * 100) + '%';
            },            
            low: 0,
            high: 8,
            fullWidth: false,
            showLabel: false,
            plugins: [
                Chartist.plugins.tooltip()
            ],
        });         
    }

    if($('.ct-chart-sales-value').length) {
        new Chartist.Line('.ct-chart-sales-value', {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            series: [
                [0, 10, 30, 50, 80, 50, 30]
            ]
            }, {
            low: 0,
            showArea: true,
            fullWidth: true,
            plugins: [
                Chartist.plugins.tooltip()
            ],
            axisX: {
                // On the x-axis start means top and end means bottom
                position: 'end',
                showGrid: false
            },
            axisY: {
                // On the y-axis start means left and end means right
                showGrid: true,
                showLabel: true,
                labelInterpolationFnc: function(value) {
                    return '$' + (value / 1) + 'k';
                }
            }
            });
    }

    if($('.ct-chart-volumes').length) {
        new Chartist.Line('.ct-chart-volumes', {
            labels: ['Mar 16', 'Apr 16', 'May 16', 'Jun 16', 'Jul 16', 'Aug 16', 'Sept 16'],
            series: [
                [2, 5, 2, 3, 4, 6, 8],
                [5, 6, 5, 8, 12, 32, 28],
                [7, 12, 7, 3, 2, 7, 14],
                [10, 15, 13, 17, 14, 18, 20],
                [16, 18, 18, 20, 20, 20, 23]
            ]
            }, {
            low: 0,
            showArea: false,
            fullWidth: true,
            plugins: [
                Chartist.plugins.tooltip()
            ],
            axisX: {
                // On the x-axis start means top and end means bottom
                position: 'end',
                showGrid: false
            },
            axisY: {
                // On the y-axis start means left and end means right
                showGrid: true,
                showLabel: true,
                labelInterpolationFnc: function(value) {
                    return (value / 1) + 'M';
                }
            }
            });
    }

    if($('.ct-chart-app-ranking').length) {
        //Chart 5
            new Chartist.Bar('.ct-chart-app-ranking', {
            labels: ['21 Apr', '21 Ap', '22 Ap', '23 Ap', '24 Ap', '25 Ap', '26 Ap'],
            series: [
                [5, 4, 3, 7, 5, 10, 3],
                [2, 2, 1, 5, 3, 4, 2],
                [3, 2, 9, 5, 4, 6, 4]
            ]
            }, {
            low: 0,
            showArea: true,
            plugins: [
                Chartist.plugins.tooltip()
            ],
            axisX: {
                // On the x-axis start means top and end means bottom
                position: 'end'
            },
            axisY: {
                // On the y-axis start means left and end means right
                showGrid: false,
                showLabel: false,
                offset: 0
            }
        });
    }

    if($('.ct-chart-traffic-share').length) {
        var data = {
            series: [30, 70]
            };
            
            var sum = function(a, b) { return a + b };
            
            new Chartist.Pie('.ct-chart-traffic-share', data, {
            labelInterpolationFnc: function(value) {
                return Math.round(value / data.series.reduce(sum) * 100) + '%';
            },            
            low: 0,
            high: 8,
            fullWidth: true,
            donut: true,
            donutWidth: 20,
            donutSolid: true,
            startAngle: 50,
            showLabel: false,
            plugins: [
                Chartist.plugins.tooltip()
            ],
        });         
    }

    if($('.ct-chart-traffic-share-2').length) {
        var data = {
            series: [51.5, 29.4, 9.10, 6.5, 3.5]
            };
            
            var sum = function(a, b) { return a + b };
            
            new Chartist.Pie('.ct-chart-traffic-share-2', data, {
            labelInterpolationFnc: function(value) {
                return Math.round(value / data.series.reduce(sum) * 100) + '%';
            },            
            low: 0,
            high: 8,
            donut: true,
            donutWidth: 40,
            fullWidth: false,
            showLabel: false,
            plugins: [
                Chartist.plugins.tooltip()
            ],
        });         
    }

    if($('.ct-chart-10').length) {
        new Chartist.Pie('.ct-chart-10', {
            series: [20, 10, 30, 40]
            }, {
            donut: true,
            donutWidth: 60,
            donutSolid: true,
            startAngle: 270,
            total: 200,
            plugins: [
                Chartist.plugins.tooltip()
            ],
            showLabel: true
        });         
    }

    if($('.ct-chart-distribution').length) {
        var data = {
            series: [30, 50, 20]
            };
            
            var sum = function(a, b) { return a + b };
            
            new Chartist.Pie('.ct-chart-distribution', data, {
            labelInterpolationFnc: function(value) {
                return Math.round(value / data.series.reduce(sum) * 100) + '%';
            },            
            low: 0,
            high: 8,
            fullWidth: true,
            donut: true,
            donutWidth: 70,
            donutSolid: true,
            startAngle: 50,
            showLabel: true,
            plugins: [
                Chartist.plugins.tooltip()
            ],
        });         
    }

    //vmap
    if($('#vmap').length) {
        $('#vmap').vectorMap(
            {
                map: 'world_en',
                backgroundColor: '#ffffff',
                borderColor: '#ffffff',
                borderOpacity: 0,
                borderWidth: 2,
                color: '#e9ecef',
                enableZoom: true,
                hoverColor: '#0E1B48',
                hoverOpacity: null,
                normalizeFunction: 'linear',
                scaleColors: ['#b6d6ff', '#005ace'],
                selectedColor: '#0E1B48',
                selectedRegions: null,
                showTooltip: true,
                onLabelShow: function(event, label, code)
                {
                label.text(label.text() + ': ' + Math.floor((Math.random() * 10000) + 1) + ' session');
                }
            });
    }

    //Countdown
    $('#clock').countdown('2020/10/10').on('update.countdown', function (event) {
        var $this = $(this).html(event.strftime(''
            + '<span>%-w</span> week%!w '
            + '<span>%-d</span> day%!d '
            + '<span>%H</span> hr '
            + '<span>%M</span> min '
            + '<span>%S</span> sec'));
    });

    //Smooth scroll
    var scroll = new SmoothScroll('a[href*="#"]', {
        speed: 500,
        speedAsDuration: true
    });

    // update target element content to match number of characters
    $('[data-bind-characters-target]').each(function () {
        var $text = $($(this).attr('data-bind-characters-target'));
        var maxCharacters = parseInt($(this).attr('maxlength'));
        $text.text(maxCharacters);

        $(this).on('keyup change', function (e) {
            var string = $(this).val();
            var characters = string.length;
            var charactersRemaining = maxCharacters - characters;
            $text.text(charactersRemaining);
        })
    });

    // copy docs
    $('.copy-docs').on('click', function () {
        var $copy = $(this);
        var htmlEntities = $copy.parents('.nav-wrapper').siblings('.card').find('.tab-pane:last-of-type').html();
        var htmlDecoded = $('<div/>').html(htmlEntities).text().trim();

        var $temp = $('<textarea>');
        $('body').append($temp);
        console.log(htmlDecoded);
        $temp.val(htmlDecoded).select();
        document.execCommand('copy');
        $temp.remove();

        $copy.text('Copied!');
        $copy.addClass('copied');

        setTimeout(function () {
            $copy.text('Copy');
            $copy.removeClass('copied');
        }, 1000);
    });

    $('.current-year').text(new Date().getFullYear());

});

