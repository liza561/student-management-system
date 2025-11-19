
importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/7.14.6/firebase-messaging.js");

firebase.initializeApp({
    apiKey: "AIzaSyBt_Y9i-IFukYyYG5wehf7RXI-4OzxBv7k",
    authDomain: "student-1067a.firebaseapp.com",
    databaseURL: "",
    projectId: "student-1067a",
    storageBucket: "student-1067a.appspot.com",
    messagingSenderId: "730276390744",
    appId: "1:730276390744:web:1967bc8d0fa2c95887a72d",
    measurementId: "G-CS6R1WGE6Y"
});

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function (payload) {
    console.log(payload);
    const notification = payload.notification;

    const notificationOption = {
        body: notification.body,
        icon: notification.icon
    };

    return self.registration.showNotification(notification.title, notificationOption);
});
