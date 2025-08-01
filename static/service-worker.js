const CACHE_NAME = 'controle-estoque-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/img/logo.png',
  // adicione outras rotas e arquivos estáticos importantes aqui
];

// Instalando o Service Worker e armazenando os arquivos no cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// Interceptando requisições para servir do cache
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});

self.addEventListener("install", function (event) {
  console.log("Service Worker instalado");
});

self.addEventListener("fetch", function (event) {
  // Poderia adicionar cache aqui se quiser suporte offline
});
