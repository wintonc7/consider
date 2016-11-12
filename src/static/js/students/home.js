function redirect(key, group) {
  if (Number(group) === 0)
  {
    location.href = '/error?code=106'
  }
  else {
    location.href = '/student_rounds?section=' + key;
  }
}
