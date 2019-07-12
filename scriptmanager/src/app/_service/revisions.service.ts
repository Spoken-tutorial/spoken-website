import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})
export class RevisionsService {
  public env = environment;
  public apiUrl = this.env['apiUrlScript']
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
  public getRevisions(sid) {
    const _url = `${this.apiUrl}/scripts/${sid}/reversions/`
    return this.http.get(_url);
  }

  public revertRevision(sid, rid) {
    const _url = `${this.apiUrl}/scripts/${sid}/reversions/${rid}/`
    console.log(_url);
    var ls = this.http.patch(
      _url,
      {},
      this.httpOptions
    );
    return ls;
  }
}
