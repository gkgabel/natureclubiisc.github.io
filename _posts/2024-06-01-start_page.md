---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: articles
mode: immersive
title: start page
show_title: false
header:
  theme: dark
article_header:
  type: overlay
  theme: dark
  background_color: '#203028'
  background_image:
    gradient: 'linear-gradient(135deg, rgba(34, 139, 87 , .4), rgba(139, 34, 139, .4))'
    src: /docs/assets/images/cover3.jpg
---




<style>
    .swiper-demo {
      height: 220px;
    }
</style>

<script>
    {%- include scripts/lib/swiper.js -%}
    var SOURCES = window.TEXT_VARIABLES.sources;
    window.Lazyload.js(SOURCES.jquery, function() {
    $('.swiper-demo').swiper();
    });
</script>


<div class="swiper swiper-demo">
    <div class="swiper__wrapper">
      <div class="swiper__slide">1</div>
      <div class="swiper__slide">2</div>
      <div class="swiper__slide">3</div>
      <div class="swiper__slide">4</div>
      <div class="swiper__slide">5</div>
      <div class="swiper__slide">6</div>
      <div class="swiper__slide">7</div>
    </div>
    <div class="swiper__button swiper__button--prev fas fa-chevron-left"></div>
    <div class="swiper__button swiper__button--next fas fa-chevron-right"></div>
</div>




Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi non neque vitae tellus eleifend hendrerit. Quisque ultricies pellentesque dui, id tristique eros suscipit eget. Suspendisse pretium metus ut imperdiet suscipit. Curabitur quis mauris nec mauris auctor lacinia. Ut vestibulum quam vitae mi placerat elementum. Proin non ligula ex. Phasellus maximus, nulla nec tempus gravida, nulla urna pulvinar leo, eu vestibulum justo sem eget mi. Sed ut tortor in nulla iaculis tincidunt. Pellentesque congue purus in lorem rhoncus, sed bibendum nunc molestie. Donec eros ex, mollis a lectus vitae, tincidunt mattis metus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi semper vitae nulla quis venenatis. Maecenas in nisl eget nibh consectetur vulputate. Suspendisse justo mauris, vehicula quis rhoncus ac, pellentesque non nulla. Duis nulla ex, blandit id laoreet et, suscipit eu turpis.

Suspendisse potenti. Nam eu volutpat odio. Nullam dictum dapibus tristique. Fusce suscipit, nibh vitae tincidunt ultrices, leo mi vestibulum ex, sed molestie tellus neque sit amet eros. Nam vel lobortis odio. In porta lacus libero, commodo lobortis purus hendrerit eu. Duis volutpat nunc non libero rhoncus mollis. Etiam turpis massa, fringilla et molestie ac, varius eu nunc. Cras sit amet ultrices ante. Morbi et ipsum sit amet tortor hendrerit aliquet vel nec urna. Fusce maximus leo a faucibus molestie. Morbi nec congue mi. Aliquam erat volutpat. Nulla et dapibus urna, vitae dignissim erat. Cras ac est venenatis, dictum libero sed, consectetur nisl. Vivamus porttitor iaculis molestie.