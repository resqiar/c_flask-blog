// username input and error DOM element definitions.
const usernameInput = document.getElementById("register-username-input");
const usernameError = document.getElementById("register-username-error");

// password input and error DOM element definitions.
const passwordInput = document.getElementById("register-password-input");
const passwordError = document.getElementById("register-password-error");

/**
 * Keep track of user key-up events
 * on the defined input. When users press any key
 * or input a character, the event is fired and the
 * corresponding function will be executed as well.
 */
usernameInput.addEventListener("keyup", handleUsernameCheck);
passwordInput.addEventListener("keyup", handlePasswordCheck);

// default error state, will be updated accordingly.
let usernameErrorState = false;
let passwordErrorState = false;

/**
 * Check whether the current username is valid
 * or is available in the database. Username must be
 * unique and the server must not accept existed username.
 * @param {KeyboardInputEvent} e
 */
async function handleUsernameCheck(e) {
  const username = e.target.value;

  // If username is not specified or less than 3 characters
  if (!username || username.length < 3) {
    // Set error and return error
    setError("username", "username must be at least 3 characters", true);
    return (usernameErrorState = true);
  }

  /**
   * Call server to check if the username is
   * available or not. Available username means
   * that the returned value MUST BE null.
   */
  const isMatch = await axios.post("/check-username", {
    username: username,
  });

  // If the username exist (not available)
  if (isMatch.data.user) {
    // Set error and return error
    setError("username", "username already exist", true);
    return (usernameErrorState = true);
  } else {
    // Reset error
    setError("username", "", true, " ");
    return (usernameErrorState = false);
  }
}

/**
 * Check whether the password is valid or not.
 * Valid password must be at least 5 characters long
 * and at least 1 letter is uppercase.
 * @param {KeyboardInputEvent} e
 */
function handlePasswordCheck(e) {
  const password = e.target.value;

  /**
   * Check if password is present
   * and the length is not less than 5 characters long.
   */
  if (!password || password.length < 5) {
    // set error and return error
    setError("password", "password must be at least 5 characters", true);
    return (passwordErrorState = true);
  }

  /**
   * Match all uppercase letter inside password
   * using Regular Expression. This will return
   * array of letter which format is uppercase.
   */
  const isContainUppercase = password.match(/[A-Z]/g);

  /**
   * If uppercase array is null or the length is
   * zero, return error.
   */
  if (!isContainUppercase || isContainUppercase.length === 0) {
    // Set error and return error
    setError(
      "password",
      "password must contain at least 1 uppercase letter",
      true
    );
    return (passwordErrorState = true);
  }

  // Reset error
  setError("password", "", true, " ");
  return (passwordErrorState = false);
}

/**
 * Simple function to modify DOM element.
 * @param {"username" | "password"} type
 * @param {String} error
 * @param {Boolean} isTriggerStyle
 * @param {String} customStyle
 */
function setError(type, error, isTriggerStyle, customStyle) {
  if (type === "username") {
    usernameError.innerHTML = error;
    if (isTriggerStyle) {
      usernameInput.style = customStyle ? customStyle : "border: 2px solid red";
    }
  } else if (type === "password") {
    passwordError.innerHTML = error;
    if (isTriggerStyle) {
      passwordInput.style = customStyle ? customStyle : "border: 2px solid red";
    }
  }
}

// form DOM element definitions.
const registerForm = document.getElementById("register-form");

/**
 * Keep track of form submit events
 * When users press register, submit event is fired and the
 * corresponding function will be executed as well.
 */
registerForm.addEventListener("submit", handleRegisterSubmit);

function handleRegisterSubmit(e) {
  /**
   * Prevent form from submitting with default behavior.
   * With this, we can intercept or rather check the input
   * if there is any error then we can simply cancel the event.
   */
  e.preventDefault();
  if (usernameErrorState || passwordErrorState) return;
  return registerForm.submit();
}
