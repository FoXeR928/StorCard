function refreshUsersTable() {
    UserAPI.getAll().done(res => {
        if (res.result) {
            const html = res.users.map(user => renderUserRow(user)).join('');
            $("#table_block_users").html(html);
        }
    });
}