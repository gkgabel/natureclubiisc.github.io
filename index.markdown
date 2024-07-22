---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
mode: normal
type: article
key: start_1909
lang: en
author: 
show_title: false
show_date: false
header: true
article_header:
  type: overlay
  background_image:
    src: /iisc.webp
#sidebar:
#  nav: docs-en
---
<header>
<nav>
<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>
</nav>
</header>

<style>

header {
  background-color: #ed7c53;
  color: #fff;
  padding: 1rem;
  <!-- position: fixed; -->
  top: 0;
  left: 0;
  width: 100%;
  z-index: 999;
}

nav ul {
  display: flex;
  justify-content: center;
  list-style-type: none;
  margin: 0;
  padding: 0;
}

nav li {
  margin: 0 1rem;
}

nav a {
  color: #fff;
  text-decoration: none;
}

nav a:hover {
  color: #ccc;
}
</style>
```yml
## _data/navigation.yml
header:
  - titles:
      en:       Archive
      zh:       归档
      zh-Hans:  归档
      zh-Hant:  歸檔
    url:        /blog/archive.html
  - titles:
      en:       About
      zh:       关于
      zh-Hans:  关于
      zh-Hant:  關於
    url:        /blog/about.html
```

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi non neque vitae tellus eleifend hendrerit. Quisque ultricies pellentesque dui, id tristique eros suscipit eget. Suspendisse pretium metus ut imperdiet suscipit. Curabitur quis mauris nec mauris auctor lacinia. Ut vestibulum quam vitae mi placerat elementum. Proin non ligula ex. Phasellus maximus, nulla nec tempus gravida, nulla urna pulvinar leo, eu vestibulum justo sem eget mi. Sed ut tortor in nulla iaculis tincidunt. Pellentesque congue purus in lorem rhoncus, sed bibendum nunc molestie. Donec eros ex, mollis a lectus vitae, tincidunt mattis metus. Interdum et malesuada fames ac ante ipsum primis in faucibus. Morbi semper vitae nulla quis venenatis. Maecenas in nisl eget nibh consectetur vulputate. Suspendisse justo mauris, vehicula quis rhoncus ac, pellentesque non nulla. Duis nulla ex, blandit id laoreet et, suscipit eu turpis.

Suspendisse potenti. Nam eu volutpat odio. Nullam dictum dapibus tristique. Fusce suscipit, nibh vitae tincidunt ultrices, leo mi vestibulum ex, sed molestie tellus neque sit amet eros. Nam vel lobortis odio. In porta lacus libero, commodo lobortis purus hendrerit eu. Duis volutpat nunc non libero rhoncus mollis. Etiam turpis massa, fringilla et molestie ac, varius eu nunc. Cras sit amet ultrices ante. Morbi et ipsum sit amet tortor hendrerit aliquet vel nec urna. Fusce maximus leo a faucibus molestie. Morbi nec congue mi. Aliquam erat volutpat. Nulla et dapibus urna, vitae dignissim erat. Cras ac est venenatis, dictum libero sed, consectetur nisl. Vivamus porttitor iaculis molestie.