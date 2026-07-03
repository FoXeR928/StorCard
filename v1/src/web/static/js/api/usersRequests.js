const UserAPI = {
    getAll: () => apiCall('/users/get', 'GET'),
    register: (data) => apiCall('/users/registration', 'POST', data),
    updatePassword: (data) => apiCall('/users/change/password', 'PATCH', data)
};

async function get_users() {
    try {
        const data = await UserAPI.getAll();
        if (!data) return;
        const { result, users, category, message } = data;
        if (result === false) {
            return create_flash(category, message);
        }
        const $select = $("#update_card_own").empty()
            .append(new Option("Выбрать пользователя", "", true, true));
        const rows = users.map(user => {
            $select.append(new Option(user.user_name, user.login));
            return userRowTemplate(user);
        }).join('');
        $("#table_block_users").html(rows);
        $("#update_card_own option:first").prop({ disabled: true, hidden: true });
    } catch (err) {
        create_flash("error", "Список пользователей не получен");
    }
}

async function update_user() {
    const login = $("#update_login").val();
    const roleVal = $("#update_user_role").val();
    const pass = $("#update_password").val();
    const passCheck = $("#update_password_check").val();
    if (!login) return;
    const tasks = [];
    if (pass) {
        if (pass.length < 8 || pass !== passCheck) {
            return create_flash("warning", "Пароли не совпадают или слишком короткие");
        }
        tasks.push(UserAPI.updatePassword({ login, password: pass }));
    }
    if (roleVal !== null) {
        tasks.push(UserAPI.updateRole({ login, isAdmin: roleVal == 1 }));
    }
    if (tasks.length === 0) return;
    try {
        const results = await Promise.all(tasks);
        results.forEach(res => {
            if (res) create_flash(res.category, res.message);
        });
        close_form_update();
        get_users();
        $("#update_password, #update_password_check").val("");
    } catch (err) {
        create_flash("error", "Произошла ошибка при обновлении");
    }
}

async function update_user() {
    const login = $("#update_login").val();
    const roleVal = $("#update_user_role").val();
    const pass = $("#update_password").val();
    const passCheck = $("#update_password_check").val();
    if (!login) return;
    const tasks = [];
    if (pass) {
        if (pass.length < 8 || pass !== passCheck) {
            return create_flash("warning", "Пароли не совпадают или слишком короткие");
        }
        tasks.push(UserAPI.updatePassword({ login, password: pass }));
    }
    if (roleVal !== null) {
        tasks.push(UserAPI.updateRole({ login, isAdmin: roleVal == 1 }));
    }
    if (tasks.length === 0) return;
    try {
        const results = await Promise.all(tasks);
        results.forEach(res => {
            if (res) create_flash(res.category, res.message);
        });
        close_form_update();
        get_users();
        $("#update_password, #update_password_check").val("");
    } catch (err) {
        create_flash("error", "Произошла ошибка при обновлении");
    }
}
