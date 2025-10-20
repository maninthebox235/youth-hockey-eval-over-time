const CACHE_NAME = 'hockey-eval-v1'
const API_CACHE = 'hockey-eval-api-v1'

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS)
    })
  )
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== API_CACHE)
          .map((name) => caches.delete(name))
      )
    })
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  if (request.method !== 'GET') {
    return
  }

  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE).then((cache) => {
        return fetch(request)
          .then((response) => {
            if (response.ok) {
              cache.put(request, response.clone())
            }
            return response
          })
          .catch(() => {
            return cache.match(request).then((cachedResponse) => {
              if (cachedResponse) {
                return cachedResponse
              }
              return new Response(JSON.stringify({ error: 'Offline' }), {
                status: 503,
                headers: { 'Content-Type': 'application/json' }
              })
            })
          })
      })
    )
  } else {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse
        }
        return fetch(request).then((response) => {
          if (response.ok) {
            return caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, response.clone())
              return response
            })
          }
          return response
        })
      })
    )
  }
})

self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-evaluations') {
    event.waitUntil(syncEvaluations())
  }
})

async function syncEvaluations() {
  const cache = await caches.open(API_CACHE)
  const requests = await cache.keys()
  
  for (const request of requests) {
    if (request.method === 'POST' && request.url.includes('/api/evaluations')) {
      try {
        await fetch(request.clone())
        await cache.delete(request)
      } catch (error) {
        console.error('Sync failed:', error)
      }
    }
  }
}
