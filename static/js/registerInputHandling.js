// username input and error DOM element definitions.
const usernameInput = document.getElementById("register-username-input");
const usernameError = document.getElementById("register-username-error");

// password input and error DOM element definitions.
const passwordInput = document.getElementById("register-password-input");
const passwordError = document.getElementById("register-password-error");

/**
 * Keep track of user key-down events
 * on the defined input. When users press any key
 * or input a character, the event is fired and the
 * corresponding function will be executed as well.
 */
usernameInput.addEventListener("keydown", handleUsernameCheck);
passwordInput.addEventListener("keydown", handlePasswordCheck);

/**
 * Check whether the current username is valid
 * or is available in the database. Username must be
 * unique and the server must not accept existed username.
 * @param {KeyboardInputEvent} e
 * @returns Promise boolean
 */
async function handleUsernameCheck(e) {
  const username = e.target.value;

  // If username is not specified or less than 3 characters
  if (!username || username.length < 3) {
    setUsernameError("username must be at least 3 characters", true);
    return false;
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
    // Set error and return false
    setUsernameError("username already exist", true);
    return false;
  } else {
    // Reset error and return true
    setUsernameError("", true, " ");
    return true;
  }
}

/**
 * Simple function to modify DOM element.
 * @param {String} error
 * @param {Boolean} isTriggerStyle
 * @param {String} customStyle
 */
function setUsernameError(error, isTriggerStyle, customStyle) {
  usernameError.innerHTML = error;
  if (isTriggerStyle) {
    usernameInput.style = customStyle ? customStyle : "border: 2px solid red";
  }
}

function handlePasswordCheck(e) {
  console.log(e.target.value);
}
