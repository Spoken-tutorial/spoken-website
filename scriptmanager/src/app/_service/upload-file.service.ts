import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})

export class UploadFileService {
  public env = environment;
  public apiUrl = this.env['apiUrlScript']
  public testData: FormData = new FormData();
  private httpOptions: any;

  constructor(private http: HttpClient, private _cookieService: CookieService) {
    let csrf = this._cookieService.get("csrftoken");
    if (typeof (csrf) === 'undefined') {
      csrf = '';
    }
    this.httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json', 'X-CSRFToken': csrf })
    };
  }

  public postFile(tid, lid, file) {
    this.testData.append('docs', file);
    this.testData.append('type', 'file');
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    return this.http.post(
      _url,
      this.testData,
      this.httpOptions,
    )
  }

}
