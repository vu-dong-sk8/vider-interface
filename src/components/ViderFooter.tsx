export function ViderFooter() {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex flex-col md:flex-row justify-between items-start gap-12">
          <div>
            <div className="text-display text-2xl tracking-widest mb-3">VIDER</div>
            <p className="text-background/50 text-sm max-w-xs">
              Trợ lý AI thế hệ mới. Nhanh, thông minh, bảo mật.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-12 text-sm">
            <div>
              <h4 className="text-label text-background/40 mb-4">Sản Phẩm</h4>
              <ul className="space-y-2 text-background/60">
                <li><a href="#features" className="hover:text-background transition-colors">Tính năng</a></li>
                <li><a href="#pricing" className="hover:text-background transition-colors">Bảng giá</a></li>
                <li><a href="#" className="hover:text-background transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-label text-background/40 mb-4">Hỗ Trợ</h4>
              <ul className="space-y-2 text-background/60">
                <li><a href="#" className="hover:text-background transition-colors">Tài liệu</a></li>
                <li><a href="#" className="hover:text-background transition-colors">Liên hệ</a></li>
                <li><a href="#" className="hover:text-background transition-colors">Blog</a></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-16 pt-8 border-t border-background/10 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-background/30 text-xs">© 2026 VIDER. All rights reserved.</p>
          <div className="flex gap-6 text-background/30 text-xs">
            <a href="#" className="hover:text-background/60 transition-colors">Privacy</a>
            <a href="#" className="hover:text-background/60 transition-colors">Terms</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
