<!-- ---
layout: article
title: Sample Event 1
hide: true
image:
one_line_detail: Details about Event 1
date: 2024-07-01
---

{% if page.title %}
  {% assign event_dir_name = page.title | downcase | replace: " ", "_" %}
  {{ event_dir_name }}
  {% assign filtered_files = "" %}
  {% for file in site.static_files %}
    {% if file.path contains '/event_images/' and file.path contains event_dir_name %}
      {% assign filtered_files = filtered_files | append: file.path | append: "," %}
    {% endif %}
  {% endfor %}
  {% assign image_files = filtered_files | split: "," %}
{% endif %}

<style>
  /* Modern Swiper Gallery Styling */
  .event-gallery {
    width: 100%;
    max-width: 1200px;
    margin: 2rem auto;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    position: relative;
  }
  
  .event-gallery .swiper__wrapper {
    height: 450px;
  }
  
  .event-gallery .swiper__slide {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f8f9fa;
    overflow: hidden;
    position: relative;
  }
  
  .event-gallery .swiper__slide img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }
  
  .event-gallery .swiper__slide:hover img {
    transform: scale(1.05);
  }
  
  .event-gallery .swiper__button {
    background-color: rgba(255, 255, 255, 0.8);
    color: #333;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    transition: all 0.3s ease;
    z-index: 10;
  }
  
  .event-gallery .swiper__button:hover {
    background-color: rgba(255, 255, 255, 1);
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
    cursor: pointer;
  }
  
  .event-gallery .swiper__pagination {
    position: absolute;
    bottom: 15px;
    left: 0;
    right: 0;
    text-align: center;
    z-index: 5;
  }
  
  .event-gallery .swiper__pagination-bullet {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.7);
    opacity: 0.7;
    margin: 0 5px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .event-gallery .swiper__pagination-bullet-active {
    background-color: #fff;
    opacity: 1;
    width: 12px;
    height: 12px;
  }
  
  /* Caption styling */
  .image-caption {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0));
    color: white;
    padding: 20px;
    text-align: left;
    opacity: 0;
    transition: opacity 0.3s ease;
  }
  
  .swiper__slide:hover .image-caption {
    opacity: 1;
  }
  
  /* Responsive adjustments */
  @media (max-width: 768px) {
    .event-gallery .swiper__wrapper {
      height: 300px;
    }
    
    .event-gallery .swiper__button {
      width: 35px;
      height: 35px;
    }
  }
  
  @media (max-width: 480px) {
    .event-gallery .swiper__wrapper {
      height: 250px;
    }
    
    .event-gallery .swiper__button {
      width: 30px;
      height: 30px;
      font-size: 0.8rem;
    }
  }
</style>

<div class="event-gallery swiper my-3">
  <div class="swiper__wrapper">
    {% for file in image_files %}
    <div class="swiper__slide">
      <img class="lightbox-ignore" src="{{ file }}" alt="Event photo {{ forloop.index }}"/>
      <div class="image-caption">
        <h4>Image {{ forloop.index }}</h4>
        <p><!-- You can add dynamic captions here later --></p>
      </div>
    </div>
    {% endfor %}
  </div>
  <div class="swiper__button swiper__button--prev fas fa-chevron-left"></div>
  <div class="swiper__button swiper__button--next fas fa-chevron-right"></div>
  <div class="swiper__pagination"></div>
</div>

<script>
  {%- include scripts/lib/swiper.js -%}
  var SOURCES = window.TEXT_VARIABLES.sources;
  window.Lazyload.js(SOURCES.jquery, function() {
    // Initialize swiper
    var mySwiper = $('.event-gallery').swiper();
    
    // Setup autoplay functionality
    var autoplayInterval;
    
    function startAutoplay() {
      autoplayInterval = setInterval(function() {
        mySwiper.next();
      }, 3000); // 3 second interval
    }
    
    function stopAutoplay() {
      clearInterval(autoplayInterval);
    }
    
    // Start autoplay when page loads
    startAutoplay();
    
    // Pause on hover (optional)
    $('.event-gallery').hover(
      function() { stopAutoplay(); },
      function() { startAutoplay(); }
    );
    
    // Add custom pagination
    var $gallery = $('.event-gallery');
    var $slides = $gallery.find('.swiper__slide');
    var $pagination = $gallery.find('.swiper__pagination');
    
    // Create pagination bullets
    if ($slides.length > 1) {
      for (var i = 0; i < $slides.length; i++) {
        $pagination.append('<span class="swiper__pagination-bullet"></span>');
      }
      
      // Set first bullet as active
      $pagination.find('.swiper__pagination-bullet').first().addClass('swiper__pagination-bullet-active');
      
      // Update pagination on slide change
      var onChange = function(index) {
        $pagination.find('.swiper__pagination-bullet').removeClass('swiper__pagination-bullet-active')
          .eq(index).addClass('swiper__pagination-bullet-active');
      };
      
      // Set onChange handler
      mySwiper.setOptions({
        onChange: onChange
      });
      
      // Make bullets clickable
      $pagination.on('click', '.swiper__pagination-bullet', function() {
        var index = $(this).index();
        stopAutoplay();
        mySwiper.previous(); // Reset position
        // Move to the clicked index
        for (var i = 0; i <= index; i++) {
          mySwiper.next();
        }
        startAutoplay();
      });
    }
  });
</script>

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras laoreet ac justo sit amet gravida. Suspendisse dignissim magna tellus, eget rhoncus magna egestas at. Mauris neque augue, mollis vel sem in, elementum volutpat massa. Phasellus tempus eu lectus et commodo. Pellentesque convallis tellus nec hendrerit sagittis. Aenean auctor ante neque, pretium sodales est hendrerit at. Pellentesque sed lacus urna. Nunc condimentum consequat turpis, ut hendrerit ligula. In hac habitasse platea dictumst. Proin sed blandit velit, eget pellentesque nibh. Proin viverra urna sed malesuada sagittis. Mauris vel libero tristique, vulputate tellus ac, egestas metus. Duis consectetur eleifend magna, vel commodo sem commodo id. Fusce feugiat nec velit vel sagittis. Morbi suscipit rhoncus lacinia. Nunc viverra molestie nulla, ut scelerisque urna volutpat viverra.

Praesent mollis congue posuere. Suspendisse a leo condimentum nisi tincidunt feugiat vel sit amet nulla. In hac habitasse platea dictumst. Nulla scelerisque, felis vel condimentum ultricies, augue lacus elementum ipsum, ut rutrum ligula massa eget magna. Curabitur nisi nibh, iaculis ut urna in, volutpat venenatis quam. Pellentesque imperdiet quam vel massa tincidunt, eget semper mi ultricies. Nunc iaculis blandit tristique. In in libero id tellus efficitur luctus. Curabitur elementum consectetur euismod. Phasellus sollicitudin quam nisi, nec finibus nisi ultricies ut. Praesent non placerat nibh, in dictum justo. Aenean est felis, blandit nec condimentum id, ullamcorper a arcu.

Integer elit massa, tristique non odio quis, consectetur efficitur ligula. Quisque feugiat purus mauris, vitae molestie sem vulputate viverra. Vivamus non facilisis quam, eget suscipit odio. Quisque pulvinar diam nisi, at varius nisl hendrerit ut. Interdum et malesuada fames ac ante ipsum primis in faucibus. Phasellus vel semper ligula. Sed eget ligula id nunc pretium gravida quis vel odio. Aliquam finibus pulvinar urna, sed viverra ligula sollicitudin lobortis. Donec sagittis erat ipsum, at ultricies augue convallis quis. Proin eleifend sagittis tincidunt. Suspendisse semper maximus aliquet. Sed sed aliquam purus, non maximus sapien. Quisque venenatis justo eu lacus tempus, et maximus lectus elementum.

Duis sodales mi ipsum, ut molestie magna tempor vel. In tristique ac eros in vulputate. Mauris nisl tortor, mattis ac orci eu, accumsan sodales diam. Praesent facilisis turpis in augue tristique volutpat. Morbi rutrum a mi eget eleifend. Mauris eleifend, lorem eu aliquam sollicitudin, ante purus auctor metus, sit amet lacinia nunc arcu sit amet sapien. Donec dapibus lorem venenatis, laoreet tellus ac, tincidunt diam. Duis finibus condimentum dignissim. In hac habitasse platea dictumst. Cras nibh urna, efficitur sed sagittis ac, rhoncus at enim. Nam vitae iaculis nisl.

Nullam nec justo sed enim ultricies rhoncus scelerisque vitae mi. Maecenas ornare elit ut tincidunt imperdiet. Curabitur sodales ultrices ullamcorper. Morbi nibh sem, viverra congue augue in, consequat faucibus nisl. Ut quam elit, pulvinar ut tempus pellentesque, consequat vel felis. Aliquam convallis velit quis leo sodales gravida non sed neque. Mauris justo nulla, pellentesque non diam id, vestibulum placerat metus. Duis justo libero, vestibulum non vehicula eu, molestie commodo metus. Cras nec viverra diam. Ut molestie neque lacus, vehicula rhoncus velit blandit in. Cras vitae eros ultrices, luctus urna in, convallis augue.
 -->
