document.addEventListener('DOMContentLoaded', () => {
    // Глобальные переменные
    const modalBg = document.getElementById('modalBg');
    const modalClose = document.getElementById('modalClose');
    const btnAddUser = document.getElementById('btnAddUser');
    const cardsContainer = document.getElementById('cardsContainer');

    let userForm = null;
    let btnDelete = null;
    let btnCancel = null;
    let formErrors = null;
    let togglePassword = null;
    let passwordInput = null;

    let currentUserId = null;
    let isNewUser = false;

    // Открытие модального окна
    function openModal() {
        modalBg.style.display = 'flex';
        if (formErrors) formErrors.textContent = '';
    }

    // Закрытие модального окна и сброс формы
    function closeModal() {
        modalBg.style.display = 'none';
        if (userForm) userForm.reset();
        currentUserId = null;
        isNewUser = false;
        if (btnDelete) btnDelete.style.display = 'inline-block';
    }

    // Настройка показа/скрытия пароля через глазик
    function setupTogglePassword() {
        togglePassword = document.getElementById('togglePassword');
        passwordInput = document.getElementById('id_Пароль');

        if (togglePassword && passwordInput) {
            togglePassword.addEventListener('click', () => {
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text';
                    togglePassword.style.color = '#3498db';
                } else {
                    passwordInput.type = 'password';
                    togglePassword.style.color = '#888';
                }
            });
        }
    }

    // Инициализация элементов формы и навешивание обработчиков
    function initFormElements() {
        userForm = document.getElementById('userForm');
        btnDelete = document.getElementById('btnDelete');
        btnCancel = document.getElementById('btnCancel');
        formErrors = document.getElementById('formErrors');

        setupTogglePassword();

        if (btnCancel) {
            btnCancel.addEventListener('click', closeModal);
        }
        if (modalClose) {
            modalClose.addEventListener('click', closeModal);
        }

        if (userForm) {
            userForm.addEventListener('submit', (e) => {
                e.preventDefault();
                formErrors.textContent = '';

                let url = '';
                if (isNewUser) {
                    url = '/user/add/';
                } else if (currentUserId) {
                    url = `/user/${currentUserId}/edit/`;
                } else {
                    formErrors.textContent = 'Не выбран пользователь для редактирования';
                    return;
                }

                const formData = new FormData(userForm);

                fetch(url, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    body: formData,
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        closeModal();
                        location.reload();
                    } else {
                        formErrors.textContent = JSON.stringify(data.errors);
                    }
                })
                .catch(() => {
                    formErrors.textContent = 'Ошибка сервера';
                });
            });
        }

        if (btnDelete) {
            btnDelete.addEventListener('click', () => {
                if (!currentUserId) return;
                if (confirm('Вы точно хотите удалить данного сотрудника?')) {
                    fetch(`/user/${currentUserId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            closeModal();
                            location.reload();
                        } else alert('Ошибка удаления');
                    })
                    .catch(() => alert('Ошибка удаления'));
                }
            });
        }
    }

    // Кнопка добавить нового пользователя – загружает форму создания
    btnAddUser.addEventListener('click', () => {
        isNewUser = true;
        currentUserId = null;
        openModal();

        fetch('/user/add/')
            .then(response => response.text())
            .then(html => {
                document.getElementById('modalContent').innerHTML = html;
                initFormElements();
                if (btnDelete) btnDelete.style.display = 'none';
            });
    });

    // Клик по карточке пользователя – загружает форму редактирования
    cardsContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.card');
        if (!card) return;
        currentUserId = card.getAttribute('data-id');
        isNewUser = false;
        openModal();

        fetch(`/user/${currentUserId}/edit/`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('modalContent').innerHTML = html;
                initFormElements();
                if (btnDelete) btnDelete.style.display = 'inline-block';
            });
    });

    // Закрытие модального окна при клике на фон
    modalBg.addEventListener('click', (e) => {
        if (e.target === modalBg) closeModal();
    });

    // Получение CSRF токена из cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const c = cookie.trim();
                if (c.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(c.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
