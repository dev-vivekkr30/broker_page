const successAlertPlaceholder = document.getElementById('scuccessAlertPlaceholder');
        const errorAlertPlaceholder = document.getElementById('errorAlertPlaceholder');
        
        const appendAlert = (message, type, placeholder) => {
            const wrapper = document.createElement('div');
            wrapper.className = `alert alert-${type} alert-dismissible alert-slide-in`;
            wrapper.setAttribute('role', 'alert');
        
            wrapper.innerHTML = `
                <div>${message}</div>
                <button type="button" class="btn-close" aria-label="Close"></button>
            `;
        
            // Append the alert
            placeholder.append(wrapper);
        
            // Handle the close animation manually
            const closeBtn = wrapper.querySelector('.btn-close');
            closeBtn.addEventListener('click', () => {
                wrapper.classList.remove('alert-slide-in');
                wrapper.classList.add('alert-slide-out');
        
                // Remove from DOM after animation ends
                wrapper.addEventListener('animationend', () => {
                    wrapper.remove();
                });
            });
        };
        
        document.getElementById('showAlertSuccess')?.addEventListener('click', () => {
            appendAlert('Profile updated successfully!', 'success', successAlertPlaceholder);
        });
        
        document.getElementById('showAlerterror')?.addEventListener('click', () => {
            appendAlert('An error occurred while updating profile.', 'danger', errorAlertPlaceholder);
        });