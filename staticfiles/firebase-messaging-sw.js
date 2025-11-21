// firebase-messaging-sw.js (place at your site's root so it is at /firebase-messaging-sw.js)
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.22.2/firebase-messaging-compat.js');

const firebaseConfig = {
  apiKey: "AIzaSyBt_Y9i-IFukYyYG5wehf7RXI-4OzxBv7k",
  authDomain: "student-1067a.firebaseapp.com",
  projectId: "student-1067a",
  storageBucket: "student-1067a.appspot.com",
  messagingSenderId: "730276390744",
  appId: "1:730276390744:web:1967bc8d0fa2c95887a72d"
};

firebase.initializeApp(firebaseConfig);
const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = (payload.notification && payload.notification.title) || 'Background Message Title';
  const notificationOptions = {
    body: (payload.notification && payload.notification.body) || 'Background Message body.',
    // icon: '/static/img/notification-icon.png'  // optional
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
