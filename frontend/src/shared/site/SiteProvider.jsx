import { createContext, useContext, useEffect, useState } from 'react';
import { apiRequest } from '../api/client';

// 站点全局上下文，缓存 blogTitle 避免各页面重复请求
const SiteContext = createContext({ blogTitle: 'myblog' });

export function SiteProvider({ children }) {
    const [site, setSite] = useState({ blogTitle: 'myblog' });

    useEffect(() => {
        apiRequest('/author')
            .then((data) => setSite({ blogTitle: data?.blog_title || 'myblog' }))
            .catch(() => {});
    }, []);

    return <SiteContext.Provider value={site}>{children}</SiteContext.Provider>;
}

export function useSite() {
    return useContext(SiteContext);
}
