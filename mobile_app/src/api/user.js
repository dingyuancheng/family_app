import request from '@/utils/request'

export function getMyMenus() {
  return request({ url: '/api/user/my-menus', method: 'get' })
}

export function recordMenuClick(menuId) {
  return request({ url: '/api/user/menu-click', method: 'post', data: { menu_id: menuId } })
}