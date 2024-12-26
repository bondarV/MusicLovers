$(document).ready(function () {
    // Обробка зміни стану чекбоксів
    $(document).on('change', '.user-musician-interaction', function () {
        var isChecked = $(this).prop('checked');
        var musician_id = $(this).data("musician-id");
        var reactionValue = $(this).data('reaction-value');
        console.log('Checkbox state changed:', isChecked);

        $.ajax({
            url: '/update-reaction',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                record_id: $(this).attr("data-record-id"),
                is_checked: isChecked,
                musician_id: musician_id,
                reaction_value: reactionValue,
            }),
            success: function (response) {
                console.log('Reaction updated successfully.');
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error details:", textStatus, errorThrown);
                alert("An error occurred.");
            }
        });
    });
    $(document).on('click', '.clear-passion', function () {
        var musician_id = $(this).data("musician-id");
        var reactionValue = $(this).data('reaction-value');
        console.log('Stop button clicked for reaction:', reactionValue);

        $.ajax({
            url: '/remove-reaction',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                musician_id: musician_id,
            }),
            success: function (response) {
                console.log('Reaction stopped successfully.');
                console.log(response.musician_id)
                // Переконатися, що відповідь містить musician_id
                const hatingInput = $(`#hating_${response.musician_id}`);
                const adoringInput = $(`#adoring_${response.musician_id}`);

                // Скидання вибору
                if (hatingInput.length) hatingInput.prop('checked', false);
                if (adoringInput.length) adoringInput.prop('checked', false);
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error details:", textStatus, errorThrown);
                alert("An error occurred.");
            }
        });
    });

    // Обробка пошуку
    $('#search-input').on('input', function () {
        const recordsList = document.getElementById('records-list');
        recordsList.innerHTML = ''; // Очистити список перед додаванням нових записів
        $.ajax({
            url: '/search_records',
            method: 'GET',
            contentType: 'application/json',
            data: {
                musician_id: $(this).data("musician-id"),
                search_engine_text: $(this).val(),
            },
            success: function (response) {
                response.records.forEach(record => {
                    const li = document.createElement('li');
                    li.classList.add('list-group-item');
                    li.id = `record-musician-${record.id}`;
                    li.innerHTML = `
                        ${record.title}
                        <input type="checkbox"
                               id="checkbox-song-${record.id}"
                               ${record.is_checked ? 'checked' : ''}
                               data-record-id="${record.id}"
                               class="record_selection">
                    `;
                    recordsList.appendChild(li);
                });
            },
            error: function () {
                console.error('Error fetching records.');
            }
        });
    });

    $(document).on('click', '.delete-record', function () {
        var musician_id = $(this).data("musician-id");
        var reactionValue = $(this).data('reaction-value');
        $.ajax({
            url: '/delete-directly-reaction',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                musician_id: musician_id,
                reaction_value: reactionValue,
            }),
            success: function (response) {
                var rowToRemove = document.querySelector(`#hating_display${response.musician_id}`);
                rowToRemove.remove();
            }
            ,
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error details:", textStatus, errorThrown);
                alert("An error occurred.");
            }
        });
    });

    // Делегування подій для чекбоксів
    $('#records-list').on('change', '.record_selection', function () {
        var isChecked = $(this).prop('checked');
        var userId = $('#current-user-id').val();
        console.log('Checkbox state changed:', isChecked);

        $.ajax({
            url: '/add_record_to_user',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                record_id: $(this).attr("data-record-id"),
                is_checked: isChecked,
                user_id: userId
            }),
            success: function (response) {
                console.log('Server response:', response);
                if (isChecked) {
                    if ($('#subscription-absent').length)
                        $('#subscription-absent').remove();
                    $('#subscribed-records-list').append(`
                        <li class="list-group-item" id="record-${response.record_id}">
                            ${response.record_title}
                            <button data-record-id="${response.record_id}" data-user-id="${response.user_id}" type="button" class="delete-subscription-btn btn btn-danger btn-sm">
                                <i class="bi bi-trash"></i> Delete
                            </button>
                        </li>
                    `);
                } else {
                    $(`#record-${response.record_id}`).remove();
                    if ($('#subscribed-records-list').children().length === 0) {
                        $('#subscribed-records-list').append(`<li class="list-group-item" id="subscription-absent">No subscribed records available.</li>`);
                    }
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error details:", textStatus, errorThrown);
                alert("An error occurred.");
            }
        });
    });

    // Обробка видалення підписки
    $('#subscribed-records-list').on('click', '.delete-subscription-btn', function () {
        const btn = $(this);
        btn.prop('disabled', true); // Disable the button during request

        const recordId = btn.data("record-id");
        const userId = $('#current-user-id').val();

        console.log("Deleting record for user:", userId, "with record id:", recordId);

        $.ajax({
            url: '/remove_record_from_user',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                record_id: recordId,
                user_id: userId,
            }),
            success: function (response) {
                console.log("Response:", response);

                // Remove the record from the list after successful deletion
                $(`#record-${response.record_id}`).remove();
                if ($('#subscribed-records-list').children().length === 0) {
                    $('#subscribed-records-list').append(`<li class="list-group-item" id="subscription-absent">No subscribed records available.</li>`);
                }
                // Optionally, uncheck the associated checkbox if it exists
                var checkbox_del = $(`#checkbox-song-${response.record_id}`);
                if (checkbox_del.length) {
                    checkbox_del.prop('checked', false);
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error("Error details:", textStatus, errorThrown);
                alert("An error occurred.");
            },
            complete: function () {
                btn.prop('disabled', false); // Re-enable the button
            }
        });
    });

    // Видалення даних
    let deleteDataButton = document.querySelector('#clear-data');
    let tableForSingers = document.querySelector('#table-for-singers');

    deleteDataButton.addEventListener('click', (e) => {
        e.preventDefault();
        let inputField = document.querySelector('#musician');
        if (inputField.value !== '') {
            inputField.value = '';
        }
        tableForSingers.innerHTML = '';
        document.querySelector(".add-data").remove();

        let url = new URL(window.location);
        url.searchParams.delete('musician');
        window.history.pushState({}, '', url);

        let existingMessage = document.querySelector('.message-display');
        if (existingMessage) {
            return;
        }
        let displayAnnounce = document.createElement('div');
        displayAnnounce.classList.add('message-display');
        let textParagraph = document.createElement('p');
        textParagraph.textContent = 'Ви видалили дані';
        displayAnnounce.appendChild(textParagraph);
        document.body.appendChild(displayAnnounce);
        displayAnnounce.classList.add('fade-out');
        setTimeout(() => {
            displayAnnounce.classList.add('fade');
            setTimeout(() => {
                displayAnnounce.remove();
            }, 1000);
        }, 1000);
    });

    // Управління кількістю музикантів
    let countOfMusician = document.querySelector('.range-input');
    let choseAtThatMoment = document.querySelector('.changed-stat');

    window.addEventListener('load', () => {
        const limit = sessionStorage.getItem("limit") || 1;
        countOfMusician.value = limit;
        choseAtThatMoment.innerText = `${limit}/${countOfMusician.max}`;
    });

    countOfMusician.addEventListener('change', () => {
        const newLimit = countOfMusician.value;
        choseAtThatMoment.innerText = `${newLimit}/${countOfMusician.max}`;
        sessionStorage.setItem("limit", newLimit);
    });
});
