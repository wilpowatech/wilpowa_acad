// js/main.js
// Global LinkJobs App Script
document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ LinkJobs main.js loaded");

  // ==========================
  // USER SYSTEM (localStorage)
  // ==========================
  const userKey = "lj_user_v1";

  function saveUser(user) {
    localStorage.setItem(userKey, JSON.stringify(user));
  }

  function getUser() {
    return JSON.parse(localStorage.getItem(userKey) || "null");
  }

  // ==========================
  // SIGNUP HANDLER
  // ==========================
  const signupForm = document.querySelector("#signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(signupForm).entries());
      saveUser({
        name: data.name,
        email: data.email,
        password: data.password,
        bio: "",
        location: "",
        title: "New User",
        portfolio: "",
      });
      alert("✅ Account created! You can now sign in.");
      window.location.href = "login.html";
    });
  }

  // ==========================
  // LOGIN HANDLER
  // ==========================
  const loginForm = document.querySelector("#loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(loginForm).entries());
      const stored = getUser();

      if (!stored) return alert("No account found. Please sign up first.");
      if (stored.email === data.email && stored.password === data.password) {
        localStorage.setItem("lj_logged_in", "true");
        alert("✅ Welcome back, " + stored.name + "!");
        window.location.href = "home.html";
      } else {
        alert("❌ Invalid email or password");
      }
    });
  }

  // ==========================
  // PROFILE PAGE
  // ==========================
  const profileSection = document.querySelector("#profileContainer");
  if (profileSection) {
    const user = getUser();
    if (!user) {
      profileSection.innerHTML = `
        <p class="text-gray-500">No profile found. Please <a href="signup.html" class="text-indigo-600 underline">create one</a>.</p>
      `;
    } else {
      profileSection.innerHTML = `
        <div class="flex items-center space-x-4 mb-6">
          <img src="https://i.pravatar.cc/100?u=${user.email}" class="w-20 h-20 rounded-full border">
          <div>
            <h2 class="text-2xl font-semibold">${user.name}</h2>
            <p class="text-gray-600">${user.title}</p>
            <p class="text-gray-500">${user.location || "Not specified"}</p>
          </div>
        </div>
        <h3 class="font-semibold text-indigo-600 mb-2">Bio</h3>
        <p class="text-gray-700 mb-4">${user.bio || "No bio added yet."}</p>

        <h3 class="font-semibold text-indigo-600 mb-2">Portfolio</h3>
        <p><a href="${user.portfolio || '#'}" class="text-indigo-600 underline">${user.portfolio || "Not provided"}</a></p>

        <div class="mt-6">
          <button id="editProfileBtn" class="bg-indigo-600 text-white px-4 py-2 rounded">Edit Profile</button>
          <button id="logoutBtn" class="bg-gray-100 text-gray-800 px-4 py-2 rounded ml-3">Log Out</button>
        </div>
      `;
    }

    const editBtn = document.querySelector("#editProfileBtn");
    if (editBtn) {
      editBtn.addEventListener("click", () => {
        const user = getUser();
        if (!user) return alert("No user to edit.");

        const name = prompt("Full Name:", user.name);
        const title = prompt("Job Title:", user.title);
        const bio = prompt("Bio:", user.bio);
        const location = prompt("Location:", user.location);
        const portfolio = prompt("Portfolio Link:", user.portfolio);

        const updated = { ...user, name, title, bio, location, portfolio };
        saveUser(updated);
        alert("✅ Profile updated!");
        window.location.reload();
      });
    }

    const logoutBtn = document.querySelector("#logoutBtn");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("lj_logged_in");
        alert("Logged out successfully.");
        window.location.href = "login.html";
      });
    }
  }
});
