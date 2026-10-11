(() => {
  document.querySelectorAll('[data-contact-copy]').forEach(button => button.addEventListener('click', async () => {
    const status = document.getElementById('contactStatus');
    try {
      await navigator.clipboard.writeText(button.dataset.contactCopy);
      status.textContent = button.dataset.contactCopy.includes('@') ? '邮箱已复制' : '群号已复制';
    } catch { status.textContent = '复制失败，请选中文字手动复制。'; }
  }));
})();
