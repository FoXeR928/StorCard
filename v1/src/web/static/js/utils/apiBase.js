const apiBase = async (endpoint, { method = 'GET', body = null, headers = {} } = {}) => {
    const config = {
        method,
        headers: {
            'Content-Type': 'application/json',
            ...headers,
        },
    };
    if (body) config.body = JSON.stringify(body);
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'Unknown error' }));
            throw new Error(error.message || `Error: ${response.status}`);
        }
        return await response.json();
    } catch (err) {
        console.error('API Error:', err.message);
        throw err;
    }
};
