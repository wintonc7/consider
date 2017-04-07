function redirect(key, group, round) {
  if (Number(group) === 0 && Number(round) !== 1)
  {
    location.href = '/error?code=106'
  }
  else {
    location.href = '/student_rounds?section=' + key;
  }
}

function collapse(id) {
  var card = document.getElementById(id);
  // if (card.hasChildNodes() && card.children[1].style.display == 'none') {
  //     card.children[1].style.display = 'block';
  // } else {
  //     card.children[1].style.display = 'none';
  // }
  if (card.hasChildNodes() && card.className == 'card course-card') {
      card.className = 'card course-card course-card-collapsed';
  } else {
      card.className = 'card course-card';
  }
}