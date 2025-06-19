class CustomSidebar extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
                    <div class="sidebar">
                <div class="menu-btn"><i class="bi bi-list"></i></div>
                <div class="head">
                    <div class="user-img">
                        <img class="mt-3" src="/static/images/admin/logo.svg" alt="">
                    </div>
                </div>
                <div class="nav">
                    <div class="menu w-100">
                        <ul class="p-0">
                            <li class="active"><a href="dashboard.html"><i class="bi bi-house"></i><span class="text">Dashboard</span></a></li>
                            <li><a href="users.html"><i class="bi bi-people"></i><span class="text">Users</span></a></li>
                            <li><a href="#"><i class="bi bi-database"></i><span class="text">Masters</span><i class="arrow ph-bold ph-caret-down"></i></a>
                                <ul class="sub-menu">
                                    <li><a href="ColoniesArea.html"><span class="text">Colonies/Area</span></a></li>
                                </ul>
                            </li>
                            <li><a href="report.html"><i class="bi bi-file-earmark-bar-graph"></i><span class="text">Reports</span></a></li>
                            
                        </ul>
                    </div>
                </div>
            </div>

        
        `;
    }
}

customElements.define("custom-sidebar", CustomSidebar);