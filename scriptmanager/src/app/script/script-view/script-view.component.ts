import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';

@Component({
  selector: 'app-script-view',
  templateUrl: './script-view.component.html',
  styleUrls: ['./script-view.component.sass']
})

export class ScriptViewComponent implements OnInit {
  public slides: any = [];
  private id: number;
  public foss;
  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService
  ) { }

  public viewScript() {
    this.createscriptService.getScript(
      this.id
    ).subscribe(
      (res) => {
          // for(let i =0;i<res['length'];i++){
          //   this.slides.push(res[i]);
          // }
          this.slides = res;
          console.log(res);
      },
      console.error
    );
  }
  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.viewScript();
  }

}
