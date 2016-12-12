function redirect(key, group, round) {
  if (Number(group) === 0 && Number(round) !== 1)
  {
    location.href = '/error?code=106'
  }
  else {
    location.href = '/student_rounds?section=' + key;
  }
}
