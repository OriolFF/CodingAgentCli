document.querySelectorAll('button').forEach(b => {
    b.addEventListener('click', e => { 
        if (e.target.innerHTML === 'Get Started')