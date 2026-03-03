const userRowTemplate = (user) => `
    <tr class="table_body_element_block">
        <td class="table_element search_element -td_user_login">${user.login}</td>
        <td class="table_element -td_user_name">${user.user_name}</td>
        <td class="table_element">${user.isAdmin ? 'Администратор' : 'Пользователь'}</td>
        <td class="table_element_button">
            <button onclick="open_form_update('${user.login}')" class="update_button -button">Изменить</button>
        </td>
    </tr>`;