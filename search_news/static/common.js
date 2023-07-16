 
function convertDateTime(datetime_str) {
    const datetime = new Date(datetime_str);
    const dateString = datetime.toLocaleDateString();
    const timeString = datetime.toLocaleTimeString();

    return `${dateString} (${timeString})`;
}

function prepareHistoryTableHtml(article_data) {
    if (article_data.length == 0) {
        return `<h2 class="text-center">No records found</h2>`
    }
    let table_html = '';
    article_data.forEach((val, idx) => {
        row_html = `
        <tr>
            <th scope="row">${idx+1}</th>
            <td>${val.search_str}</td>
            <td><a href="/news_article/history/articles?search_id=${val.id}" target="_blank">Open article</a></td>
            <td>${val.total_results}</td>
            <td>${convertDateTime(val.created_at)}</td>
        </tr>
        `
        table_html += row_html;
    });
    $('#search-results').show()

    return table_html;
}


function prepareUserTableHtml(data) {
    if (!data) {
        return `<h2 class="text-center">No records found</h2>`
    }
    let table_html = '';
    data.forEach((val, idx) => {
    row_html = `
        <tr>
            <td>${val.username}</td>
            <td>${val.email}</td>
            <td>${convertDateTime(val.created_at)}</td>
            <td>
                <div class="form-check form-switch">
                    <input class="form-check-input" type="checkbox" id="user_toggle" onchange="toggleUser(this, ${val.user_id})" ${val.is_active ? 'checked' : ''}>
                </div>
            </td>
        </tr>
        `
        table_html += row_html;
    });

    $('#search-results').show();
    return table_html;
}


function prepareArticleTableHtml(article_data) {
    console.log("============= : chck1: ", article_data)
    if (article_data.length === 0) {
        console.log("============= : chck2: ", article_data)
        return `<h2 class="text-center">No records found</h2>`
    }
    let table_html = '';
    article_data.forEach((val, idx) => {
        row_html = `
        <tr>
            <th scope="row">${idx+1}</th>
            <td>${val.title}</td>
            <td>${val.author}</td>
            <td>${val.description}</td>
            <td><a href="${val.url}" target="_blank">open</a></td>
            <td>${convertDateTime(val.publishedAt)}</td>
        </tr>
        `
        table_html += row_html;
    });

    $('#search-results').show();
    return table_html;
}

// Function to show the error popup
function showErrorPopup(errorMessage) {
    $('#errorMessage').text(errorMessage);
    $('#errorToast').toast('show');
    
    // Automatically hide the error popup after 3 seconds (adjust the duration as needed)
    setTimeout(closeErrorPopup, 3000);
  }

  // Function to close the error popup
function closeErrorPopup() {
    $('#errorToast').toast('hide');
}