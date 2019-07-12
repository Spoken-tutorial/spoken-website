import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment'
import { CookieService } from 'ngx-cookie';

@Injectable({
  providedIn: 'root'
})

export class CreateScriptService {
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

  public getScript(tid, lid) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    return this.http.get(_url);
  }

  public postScript(tid, lid, data) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/`
    var ls = this.http.post(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

  public patchScript(tid, lid, data) {
    let script_pk = data['id']
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${script_pk}/`
    var ls = this.http.patch(
      _url,
      data,
      this.httpOptions
    );
    return ls;
  }

  public deleteScript(tid, lid, script_pk) {
    const _url = `${this.apiUrl}/tutorial/${tid}/language/${lid}/scripts/${script_pk}/`
    var ls = this.http.delete(
      _url,
      this.httpOptions
    );
    return ls;
  }


}
