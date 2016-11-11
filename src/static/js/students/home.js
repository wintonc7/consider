function redirect(key, group) {
  if (Number(group) === 0)
  {
    location.href = '/error'
  }
  else {
    location.href = '/student_rounds?section=' + key;
  }
}
